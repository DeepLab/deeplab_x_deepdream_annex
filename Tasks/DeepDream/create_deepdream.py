from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def create_deepdream(uv_task):
	task_tag = "CREATING DEEPDREAM"
	print "\n\n************** %s [START] ******************\n" % task_tag
	print "creating deepdream for image at %s" % uv_task.doc_id
	uv_task.setStatus(302)

	from lib.Worker.Models.deepdream import DeepDream
	
	dd = DeepDream(_id=uv_task.doc_id)
	if dd is None:
		error_msg = "No DeepDream here!"
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		print error_msg
		
		uv_task.fail(message=error_msg)
		return

	# must downsample image to about 680 x 420 or whatever; i cannot do big imgs.
	if not dd.downsample():
		error_msg = "Could not downsample original image"
		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		print error_msg

		uv_task.fail(message=error_msg)
		return

	uv_task.put_next("DeepDream.iterate_deepdream.iterate_deepdream")
	dd.addCompletedTask(uv_task.task_path)

	uv_task.routeNext()
	uv_task.finish()
	print "\n\n************** %s [END] ******************\n" % task_tag

	