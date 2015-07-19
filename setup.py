import os, json, yaml
from sys import exit, argv
from fabric.api import local, settings
from fabric.operations import prompt

if __name__ == "__main__":
	base_dir = os.getcwd()
	conf_dir = os.path.join(base_dir, "lib", "Annex", "conf")

	print "****************************************"

	sec_config = {}
	if len(argv) == 2 and len(argv[1]) > 3:
		try:
			with open(argv[1], 'rb') as CONFIG: 
				sec_config.update(json.loads(CONFIG.read()))
		except Exception as e:
			pass

	if 'dropbox_root' not in sec_config.keys():
		sec_config['dropbox_root'] = os.path.join(os.path.expanduser('~'), "Dropbox", "deeplab_x_deepdream")
		
		if not os.path.exists(sec_config['dropbox_root']):
			print "WARNING: NO DROPBOX FOLDER AT %s" % sec_config['dropbox_root']

	if 'slack' not in sec_config.keys():
		sec_config['slack'] = {}

	for s in ['channel_id', 'webhook_url']:
		if s not in sec_config['slack'].keys():
			sec_config['slack'][s] = prompt("What is your Slack %s? " % s)

	if 'caffe_root' not in sec_config.keys():
		caffe_root = os.getenv('CAFFE_ROOT')
		
		if len(caffe_root) == 0:
			caffe_root = prompt("Where is Caffe installed? ")

		sec_config['caffe_root'] = caffe_root

	if 'ffmpeg' not in sec_config.keys():
		with settings(warn_only=True):
			ffmpeg = local("which ffmpeg", capture=True)

		if len(ffmpeg) == 0:
			ffmpeg =  prompt("Where is your FFMpeg binary? ")

		sec_config['ffmpeg'] = ffmpeg

	if 'xmpp' not in sec_config.keys():
		sec_config['xmpp'] = {}

	for cred in ['jid', 'pwd', 'bot_jid']:
		if cred not in sec_config['xmpp'].keys():
			sec_config['xmpp'][cred] = prompt("XMPP %s: " % cred)

	with open(os.path.join(conf_dir, "annex.config.yaml"), 'ab') as CONFIG:
		CONFIG.write("caffe_root: %s\n" % sec_config['caffe_root'])
		CONFIG.write("ffmpeg: %s\n" % sec_config['ffmpeg'])
		CONFIG.write("vars_extras: %s\n" % os.path.join(base_dir, "vars.json"))

	del sec_config['caffe_root']
	del sec_config['ffmpeg']

	try:
		with open(os.path.join(conf_dir, "unveillance.secrets.json"), 'rb') as SECRETS:
			sec_config.update(json.loads(SECRETS.read()))
	except IOError as e:
		pass

	with open(os.path.join(conf_dir, "unveillance.secrets.json"), 'wb+') as SECRETS:
		SECRETS.write(json.dumps(sec_config))

	# initial task to start xmpp client...
	initial_tasks = []
	
	try:
		with open(os.path.join(conf_dir, "initial_tasks.json"), 'rb') as I_TASKS:
			initial_tasks.extend(json.loads(I_TASKS.read()))
	except Exception as e:
		pass
		
	initial_tasks.append({
		'task_path' : "XMPP.client.create_xmpp_client",
		'queue' : os.getenv('UV_UUID')
	})

	with open(os.path.join(conf_dir, "initial_tasks.json"), 'wb+') as I_TASKS:
		I_TASKS.write(json.dumps(initial_tasks))

	exit(0)