from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def giffify_deepdream(uv_task):
	task_tag = "GIFFIFYING DEEPDREAM"
	print "\n\n************** %s [START] ******************\n" % task_tag
	print "giffifying deepdream for image at %s" % uv_task.doc_id
	uv_task.setStatus(302)

	from lib.Worker.Models.deepdream import DeepDream
	
	dd = DeepDream(_id=uv_task.doc_id)
	if dd is None:
		error_msg = "No DeepDream here!"

		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		print error_msg
		
		uv_task.fail(message=error_msg)
		return

	if not dd.giffify():
		error_msg = "Could not giffify deepdream"

		print "\n\n************** %s [ERROR] ******************\n" % task_tag
		print error_msg

		uv_task.fail(message=error_msg)
		return
	
	uv_task.routeNext()
	uv_task.finish()
	print "\n\n************** %s [END] ******************\n" % task_tag

