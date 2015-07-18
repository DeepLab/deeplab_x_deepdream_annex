from __future__ import absolute_import

from vars import CELERY_STUB as celery_app

@celery_app.task
def create_xmpp_client(uv_task):
	task_tag = "CREATING XMPP CLIENT"
	print "\n\n************** %s [START] ******************\n" % task_tag
	uv_task.setStatus(302)

	from lib.Worker.Models.xmpp_client import DLXDD_XMPP
	xmpp = DLXDD_XMPP()
	xmpp.start()

	uv_task.finish()
	print "\n\n************** %s [END] ******************\n" % task_tag

	