import pika
import uuid
import time
import json
import threading
import platform
import urllib2
import mq_handler

# Create a global channel variable to hold our channel object in
mq_handle = None

settings_dict = {'speed': 5}
settings_change = False

def upload(data):
	global settings_dict
	if data == 'true':
		print settings_dict
	return

def settings(data):
	global settings_dict
	global settings_change
	data = json.loads(data)
	settings_dict.update(data)
	settings_change = True
	print settings_change
	return

def shutdown(data):
	global run
	global connection
	global mq_handle
	if data == 'true':
		print "Shutdown received"
		run = False
		mq_handle.run = False
		mq_handle.connection.close()
	return
	
def reconnect(data):
	global connection
	global mq_handle
	if data == 'true':
		print "Reconnect received"
		mq_handle.connection.close()
	return

actions = {'shutdown': shutdown,
		   'reconnect': reconnect,
		   'settings': settings,
		   'upload': upload,
}

def monitor_thread():
	global settings_dict
	global settings_change
	while True:
		print ".",
		if settings_change:
			print settings_dict
			settings_change = False
		time.sleep(1)
		
def main():
	global mq_handle
	global actions
	
	monitor = threading.Thread(target = monitor_thread)
	monitor.daemon = True
	monitor.start()
	
	mq_handle = mq_handler.mq_handler(actions, 'device', '123')
	mq_handle.start()
	
	while mq_handle.run:
		pass
	print "Shutting down..."
	time.sleep(5)

if __name__ == "__main__":
	try:
		main()
	except KeyboardInterrupt:
		connection.close()
		connection.ioloop.start()
