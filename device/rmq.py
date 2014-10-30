import pika
import uuid
import time
import json

# Create a global channel variable to hold our channel object in
channel = None
run = True
connection = None

def shutdown(data):
	global run
	global connection
	if data == 'true':
		print "Shutdown received"
		run = False
		connection.close()
	return
	
def reconnect(data):
	global connection
	if data == 'true':
		print "Reconnect received"
		connection.close()
	return

actions = {'shutdown': shutdown,
		   'reconnect': reconnect
}

# Step #2
def on_connected(connection):
	"""Called when we are fully connected to RabbitMQ"""
	# Open a channel
	print "Connected"
	connection.channel(on_channel_open)

# Step #3
def on_channel_open(new_channel):
	"""Called when our channel has opened"""
	global channel
	print "Channel open"
	channel = new_channel
	channel.queue_declare(queue=str(uuid.getnode()), durable=False, exclusive=False, auto_delete=True, callback=on_queue_declared)

# Step #4
def on_queue_declared(frame):
	"""Called when RabbitMQ has told us our Queue has been declared, frame is the response from RabbitMQ"""
	print "Queue open"
	channel.basic_consume(handle_delivery, queue=str(uuid.getnode()))

# Step #5
def handle_delivery(channel, method, header, body):
	"""Called when we receive a message from RabbitMQ"""
	global run
	global connection
	global actions
	data = json.loads(body)
	print data
	for d in data:
		if d in actions:
			actions[d](data[d][0])

# Step #1: Connect to RabbitMQ using the default parameters
def main():
	global run
	global connection
	
	creds = pika.PlainCredentials('device', '123')
	parameters = pika.ConnectionParameters(host = '192.168.2.1', port = 5672, credentials = creds)
	
	while run:
		connection = pika.SelectConnection(parameters, on_connected)
		connection.ioloop.start()
		print "Connection closed..."
		time.sleep(5)

if __name__ == "__main__":
	try:
		# Loop so we can communicate with RabbitMQ
		main()
	except KeyboardInterrupt:
		# Gracefully close the connection
		connection.close()
		# Loop until we're fully closed, will stop on its own
		connection.ioloop.start()
