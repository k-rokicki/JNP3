from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import random
import requests

url = 'http://localhost:9200/images/image/_search?pretty'
headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}

dog_data_list = [{'title': 'Doggo', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 0, 'woofs': 4242},
                 {'title': 'Pupper', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 1, 'woofs': 424},
                 {'title': 'Woofer', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 2, 'woofs': 42},
                 {'title': 'Fluffer', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 3, 'woofs': 4}]


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
    title_for_query = ''
    tag_for_query = ''
    query = False

    if request.method == 'POST':
        query = True
        tag_for_query = request.POST.get("tag", "")
        found_dogs = get_doggos_by_term(tag_for_query)

    return render(request, 'search_doggos.html', {'found_dogs': found_dogs, 'query': query, 'title_for_query': title_for_query, 'tag_for_query': tag_for_query})
