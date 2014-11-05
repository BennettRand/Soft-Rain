import pika
import uuid
import time
import json
import threading
import platform
import urllib2
import mq_handler

_sd = None
_mq = None

settings_change = False

def init_actions(sd, mq):
	global _sd
	global _mq
	_sd = sd
	_mq = mq

def upload(data):
	global _sd
	global _mq
	if data == 'true':
		print _sd
	return

def settings(data):
	global _sd
	global _mq
	global settings_change
	data = json.loads(data)
	_sd.update(data)
	settings_change = True
	print settings_change
	return

def shutdown(data):
	global _mq
	if data == 'true':
		print "Shutdown received"
		_mq.run = False
		_mq.connection.close()
	return
	
def reconnect(data):
	global _mq
	if data == 'true':
		print "Reconnect received"
		_mq.connection.close()
	return

actions = {'shutdown': shutdown,
		   'reconnect': reconnect,
		   'settings': settings,
		   'upload': upload,
}