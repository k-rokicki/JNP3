import pika
import json

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)

path = input('Enter path to image: ')
title = input('Enter title: ')
tags = []
while True:
    tag = input('Enter tag (0 to stop adding tags): ')
    if tag == '0':
        break
    tags.append(tag)

upload_dict = {'path': path, 'title': title, 'tags': tags}

message = json.dumps(upload_dict)
channel.basic_publish(
    exchange='',
    routing_key='task_queue',
    body=message,
    properties=pika.BasicProperties(
        delivery_mode=2,  # make message persistent
    ))
print(" [x] Sent %r" % message)
connection.close()
