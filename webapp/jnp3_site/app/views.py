from django.core.files import File
from django.http import HttpResponseRedirect
from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import random
import requests
import pika
import json
from os import system
import string

url = 'http://localhost:9200/images/image/_search?pretty'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}


def copy_file_to_docker_container(file_path, docker_file_path, docker_tag):
    system(f'sudo docker cp {file_path} {docker_tag}:{docker_file_path}')


def remove_file(file_path):
    system(f'rm -f {file_path}')


def parse_response(response):
    id = response['_id']
    title = response['_source']['title']
    tags = response['_source']['tags'].split(', ')
    upvotes = response['_source']['upvotes']

    data = {}
    data['dog_id'] = int(id)
    data['title'] = title
    data['tags'] = tags
    data['woofs'] = upvotes

    return data


def get_random_doggo():
    payload = '{\
        \"size\" : 1,\
        \"query\": {\
            \"function_score\": {\
                \"random_score\": {}\
            }\
        }\
    }'

    r = requests.get(url, data=payload, headers=headers)
    response = r.json()['hits']['hits'][0]

    return parse_response(response)


def get_certain_doggo(dog_id):
    r = requests.get('http://localhost:9200/images/image/%d?pretty' %
                     dog_id, headers=headers)
    response = r.json()

    return parse_response(response)


def get_top_doggos():
    payload = '{\
        \"size\": 5,\
        \"sort\": [{\"upvotes\": \"desc\"}]\
    }'

    r = requests.get(url, data=payload, headers=headers)
    responses = r.json()['hits']['hits']

    results = []
    
    for response in responses:
        results.append(parse_response(response))
    
    return results


def get_doggos_by_term(term):
    payload = '{\
        "query": {\
            \"query_string\": {\
                \"query\": \"*%s*\",\
                \"fields\": [ \"title\", \"tags\" ]\
            }\
        }\
    }' % term

    r = requests.get(url, data=payload, headers=headers)
    responses = r.json()['hits']['hits']

    results = []

    for response in responses:
        results.append(parse_response(response))

    return results


def single_doggo(request, dog_id=None):

    if dog_id is None:
        dog_data = get_random_doggo()
    else:
        dog_data = get_certain_doggo(dog_id)

    return render(request, 'single_doggo.html', {'dog_data': dog_data})


@require_http_methods(["POST"])
@csrf_exempt
def rate_doggo(request, dog_id):

    rating = request.POST.get("rating", "")
    print(f'dog with id = {dog_id} was given {rating} woofs')

    payload = '{\
        \"script\": {\
            \"source\": \"ctx._source.upvotes += params.count\",\
            \"lang\": \"painless\",\
            \"params\": {\
                \"count\": %s\
            }\
        }\
    }' % rating

    r = requests.post('http://localhost:9200/images/_update/%d?pretty' %
                     dog_id, data=payload, headers=headers)

    return redirect(single_doggo, permanent=False)


def random_redirect(request):
    return redirect(single_doggo, permanent=True)


@csrf_exempt
def top_doggos(request):

    best_dogs_data = get_top_doggos()

    return render(request, 'top_doggos.html', {'best_dogs': best_dogs_data})


@csrf_exempt
def search_doggos(request):

    found_dogs = []
    search_phrase = ''
    query = False

    if request.method == 'POST':
        query = True
        search_phrase = request.POST.get("search_phrase", "")
        found_dogs = get_doggos_by_term(search_phrase)

    return render(request, 'search_doggos.html', {'found_dogs': found_dogs, 'query': query, 'search_phrase': search_phrase})


@csrf_exempt
def upload_doggo(request):

    if request.method == 'POST':
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='task_queue', durable=True)

        image = request.FILES['dog_image']
        title = request.POST.get("title", "")
        tags = request.POST.get("tags", "")
        name_len = 64
        request_file_name = image.name
        file_name = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(name_len))
        file_name += '.' + request_file_name.split('.')[-1]

        fout = open(f'/photos_to_upload/{file_name}', 'wb+')
        file_content = File(image)
        for chunk in file_content.chunks():
            fout.write(chunk)
        fout.close()

        upload_dict = {'server': 1, 'path': file_name, 'title': title, 'tags': tags.split(',')}

        message = json.dumps(upload_dict)
        channel.basic_publish(
            exchange='',
            routing_key='task_queue',
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # make message persistent
        ))

        connection.close()

        return HttpResponseRedirect('/upload')

    return render(request, 'upload_doggo.html')
