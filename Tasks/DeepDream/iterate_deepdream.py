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

	uv_task.put_next("DeepDream.iterate_deepdream.iterate_deepdream")
	dd.addCompletedTask(uv_task.task_path)
	
	uv_task.routeNext()
	uv_task.finish()
	print "\n\n************** %s [END] ******************\n" % task_tag

	