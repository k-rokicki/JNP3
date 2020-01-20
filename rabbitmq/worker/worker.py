#!/usr/bin/env python
import pika
import time
from PIL import Image
from os import system
import requests
import random
import json


def add_to_database(title, tags):
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    while True:
        dog_id = random.randrange(1000000000)
        r = requests.get('http://localhost:9200/images/image/%d?pretty' %
                         dog_id, headers=headers)
        response = r.json()

        if not response['found']:
            payload = '{\
                \"title\": \"%s\",\
                \"tags\": \"%s\",\
                \"upvotes\": 0\
            }' % (title, tags)

            r = requests.post('http://localhost:9200/images/image/%d' %
                              dog_id, data=payload, headers=headers)
            response = r.json()

            if response['result'] == 'created' and response['_id'] == str(dog_id):
                break
    return dog_id


def copy_file_from_webapp(webapp_folder_path, local_folder_path, entry_path):
    system('sudo docker cp webapp:%s %s' % (webapp_folder_path + entry_path, local_folder_path + entry_path))


def remove_file_from_webapp(webapp_folder_path, entry_path):
    system('sudo docker exec webapp rm -rf %s' % webapp_folder_path + entry_path)


def resize_image(path_to_file, new_height, path_to_resized_file=None):
    if path_to_resized_file is None:
        path_to_resized_file = path_to_file

    image = Image.open(path_to_file)
    new_width = float(image.size[1]) * (new_height / image.size[0])
    image.thumbnail((new_height, new_width), Image.ANTIALIAS)
    image.save(path_to_resized_file, "JPEG")


def copy_file_to_docker_container(file_path, docker_file_path, docker_tag):
    system('sudo docker cp %s %s:%s' % (file_path, docker_tag, docker_file_path))


def remove_file(file_path):
    system('rm -f %s' % file_path)


content_servers = ['serve_static_content', 'serve_static_content2']
content_folder_path = '/usr/share/nginx/html/static/content'

webapp_folder_path = '/photos_to_upload/'
local_folder_path = './photos_to_upload/'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='task_queue', durable=True)
print(' [*] Waiting for messages. To exit press CTRL+C')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)

    new_entry = json.loads(body.decode('utf-8'))
    dog_id = add_to_database(new_entry['title'], ', '.join(new_entry['tags']))

    copy_file_from_webapp(webapp_folder_path,
                          local_folder_path, new_entry['path'])

    resize_image(local_folder_path + new_entry['path'], 500)

    for content_server_tag in content_servers:
        copy_file_to_docker_container(
            local_folder_path + new_entry['path'], '%s/%s.jpg' % (content_folder_path, dog_id), content_server_tag)

    remove_file(local_folder_path + new_entry['path'])
    remove_file_from_webapp(webapp_folder_path, new_entry['path'])

    print(" [x] Done")
    ch.basic_ack(delivery_tag=method.delivery_tag)


channel.basic_qos(prefetch_count=1)
channel.basic_consume(queue='task_queue', on_message_callback=callback)

channel.start_consuming()
