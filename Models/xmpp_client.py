import os, json, logging, requests

from time import sleep
from HTMLParser import HTMLParser
from multiprocessing import Process
from sleekxmpp import ClientXMPP
from sleekxmpp.exceptions import IqError, IqTimeout
from fabric.api import settings, local

from lib.Core.Utils.funcs import stopDaemon, startDaemon
from conf import getSecrets, getConfig, ANNEX_DIR, API_PORT

class DLXDD_XMPP(ClientXMPP):
	def __init__(self):
		print "xmpp client..."
		from conf import MONITOR_ROOT

		self.log_file = os.path.join(MONITOR_ROOT, "xmpp.log.txt")
		self.pid_file = os.path.join(MONITOR_ROOT, "xmpp.pid.txt")
		self.cred = getSecrets('xmpp')

		#logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')

	def __on_session_start(self, event):
		print "XMPP session started"

		self.send_presence()
		try:
			roster = self.get_roster()
			print roster
		except Exception as e:
			print e, type(e)

	def __on_message(self, msg):
		print msg
		print msg.keys()

		print dir(msg['from'])
		print dir(msg['body'])

		if msg['from'].jid.split('/')[0] != self.cred['bot_jid']:
			print "message not from our bot"
			return

		h = HTMLParser()
		try:
			cmd = json.loads(h.unescape(msg['body']))
		except Exception as e:
			print "could not find json in message %s" % msg['body']
			print e, type(e)
			return

		print cmd
		if len(cmd.keys()) != 2 or 'task_path' not in cmd.keys():
			print "msg invalid (%s)" % msg['body']
			return

		if cmd['task_path'] == "Documents.evaluate_document.evaluateDocument":
			if 'file_name' not in cmd.keys():
				print "no file specified"
				return

			file_path = os.path.join(getSecrets('dropbox_root'), cmd['file_name'])

			while not os.path.exists(file_path):
				print "file not in dropbox yet"
				sleep(5)

			with settings(warn_only=True):
				local("cp %s %s" % (file_path, ANNEX_DIR))
				local("rm %s" % file_path)

			with settings(warn_only=True):
				whoami = local("whoami", capture=True)

			THIS_DIR = os.getcwd()

			annex_cmd = [
				".git/hooks/uv-post-netcat",
				"\"%s\"" % cmd['file_name'],
				"--importer_source=xmpp",
				"--imported_by=%s" % whoami
			]

			os.chdir(ANNEX_DIR)
			
			with settings(warn_only=True):
				local(" ".join(annex_cmd))
			
			os.chdir(THIS_DIR)

		else:
			req = "http://localhost:%d/reindex/?_id=%s&task_path=%s" % (API_PORT, cmd['doc_id'], cmd['task_path'])
			print req

			try:
				r = requests.get(req)
			except Exception as e:
				print "Could not do request"
				print e, type(e)

	def create(self):
		ClientXMPP.__init__(self, self.cred['jid'], self.cred['pwd'])

		for plugin in ['xep_0030', 'xep_0199', 'xep_0060']:
			self.register_plugin(plugin)

		self.add_event_handler("session_start", self.__on_session_start)
		self.add_event_handler("message", self.__on_message)

		startDaemon(self.log_file, self.pid_file)
		print "attempting connections..."
		connect = self.connect()
		print "connected?"
		print connect

		if connect:
			self.process(block=True)

	def start(self):
		p = Process(target=self.create)
		p.start()

	def stop(self):
		print "stopping xmpp server"
		stopDaemon(self.pid_file)