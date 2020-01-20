#!/usr/bin/env python
import pika
import time
from PIL import Image
from os import system


def resize_image(path_to_file, new_height, path_to_resized_file=None):
    if path_to_resized_file is None:
        path_to_resized_file = path_to_file

    image = Image.open(path_to_file)
    new_width = float(image.size[1]) * (new_height / image.size[0])
    image.thumbnail((new_height, new_width), Image.ANTIALIAS)
    image.save(path_to_resized_file, "JPEG")


def copy_file_to_docker_container(file_path, docker_file_path, docker_tag):
    system(f'sudo docker cp {file_path} {docker_tag}:{docker_file_path}')


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()
