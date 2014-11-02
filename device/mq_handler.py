import pika
import uuid
import time
import json
import threading
import platform
import urllib2

class mq_handler:
	def __init__(self, actions, un='', pw=''):
		self.creds = pika.PlainCredentials(un, pw)
		self.parameters = pika.ConnectionParameters(host = '192.168.2.1', port = 5672, credentials = self.creds)
		self.connection = None
		self.actions = actions
		self.run = True
		
		self.io = threading.Thread(target = self.ioloop_thread)
		self.io.daemon = True
		
	def on_connected(self, connection):
		print "Connected"
		self.connection.channel(self.on_channel_open)
	
	def on_channel_open(self, new_channel):
		print "Channel open"
		self.channel = new_channel
		self.channel.queue_declare(queue=str(uuid.getnode()),
								   durable=False,
								   exclusive=False,
								   auto_delete=True,
								   callback=self.on_queue_declared)
	
	def on_queue_declared(self, frame):
		print "Queue open"
		self.channel.basic_consume(self.handle_delivery, queue=str(uuid.getnode()))
	
	def handle_delivery(self, channel, method, header, body):
		data = json.loads(body)
		print data
		self.channel.basic_ack(delivery_tag = method.delivery_tag)
		for d in data:
			if d in self.actions:
				self.actions[d](data[d][0])
	
	def ioloop_thread(self):
		while self.run:
			self.connection = pika.SelectConnection(self.parameters, self.on_connected)
			self.connection.ioloop.start()
			print "Connection closed..."
			time.sleep(1)
			
	def start(self):
		self.io.start()