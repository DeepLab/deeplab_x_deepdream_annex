from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def iterate_deepdream(uv_task):
	task_tag = "ITERATING DEEPDREAM"
	print "\n\n************** %s [START] ******************\n" % task_tag
	print "iterating deepdream for image at %s" % uv_task.doc_id
	uv_task.setStatus(302)

	from lib.Worker.Models.deepdream import DeepDream
	
	dd = DeepDream(_id=uv_task.doc_id)
	if dd is None:
		error_msg = "No DeepDream here!"
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		print error_msg
		
		uv_task.fail(message=error_msg)
		return

	from time import sleep

	# iterate on the derivative twice, or number specified
	if not hasattr(uv_task, 'with_iterations'):
		num_iterations = 3
	else:
		num_iterations = uv_task.with_iterations

	for i in xrange(0, num_iterations):
		if not dd.iterate():
			error_msg = "Could not iterate (try #%d)" % i
			print "\n\n************** %s [ERROR] ******************\n" % task_tag
			print error_msg

			uv_task.fail(message=error_msg)
			return

		sleep(5)

	import os
	from vars import ASSET_TAGS

	try:
		last_dream = dd.getAssetsByTagName(ASSET_TAGS['DLXDD_DD'])[-1]
		r_file_name = "%s_%s" % (last_dream['file_name'].replace(".jpg", ""), dd.file_name)
		r_content = dd.loadFile(os.path.join(dd.base_path, last_dream['file_name']))

		if r_content is None:
			error_msg = "No deepdream found at %s" % last_dream['file_name']
			print "\n\n************** %s [ERROR] ******************\n" % task_tag
			print error_msg
			
			uv_task.fail(message=error_msg)
			return

		if not dd.post_to_slack(r_file_name, r_content, \
			title="I deepdreamed...", bot_callback="want MOAR? want GIF? my id is `%s`" % dd._id):
			
			error_msg = "Result from post not OK"
			print "\n\n************** %s [ERROR] ******************\n" % task_tag
			print error_msg
			
			uv_task.fail(message=error_msg)
			return

	except Exception as e:
		error_msg = e
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		print error_msg, type(e)
		
		uv_task.fail(message=error_msg)
		return

	dd.addCompletedTask(uv_task.task_path)	
	uv_task.routeNext()
	uv_task.finish()
	print "\n\n************** %s [END] ******************\n" % task_tag

	