import pika
import uuid
import time
import json
import threading
import platform
import urllib2
import mq_handler
import actions

# Create a global channel variable to hold our channel object in
mq_handle = None

settings_dict = {'speed': 5}

def monitor_thread():
	global settings_dict
	while True:
		print ".",
		if actions.settings_change:
			print settings_dict
			actions.settings_change = False
		time.sleep(1)
		
def main():
	global mq_handle
	global actionsd
	
	monitor = threading.Thread(target = monitor_thread)
	monitor.daemon = True
	monitor.start()
	
	mq_handle = mq_handler.mq_handler(actions.actions, 'device', '123')
	mq_handle.start()
	actions.init_actions(settings_dict, mq_handle)
	
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
