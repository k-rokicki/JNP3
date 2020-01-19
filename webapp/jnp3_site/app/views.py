from django.shortcuts import render, HttpResponse, redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

import random


dog_data_list = [{'title': 'Doggo', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 0, 'woofs': 4242},
                 {'title': 'Pupper', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 1, 'woofs': 424},
                 {'title': 'Woofer', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 2, 'woofs': 42},
                 {'title': 'Fluffer', 'tags': ['tag1', 'tag2', 'tag3', 'tag4', 'tag5', 'tag6'], 'dog_id': 3, 'woofs': 4}]


def single_doggo(request, dog_id=None):

    if dog_id is None:
        dog_id = random.randint(0, 3)  # TODO generate random id

    dog_data = dog_data_list[dog_id]

    return render(request, 'single_doggo.html', {'dog_data': dog_data})


@require_http_methods(["POST"])
@csrf_exempt
def rate_doggo(request, dog_id):

    rating = request.POST.get("rating", "")
    print(f'dog with id = {dog_id} was given {rating} woofs')

    # add rating to database

    return redirect(single_doggo, permanent=False)


def random_redirect(request):
    return redirect(single_doggo, permanent=True)


@csrf_exempt
def top_doggos(request):

    best_dogs_data = dog_data_list

    return render(request, 'top_doggos.html', {'best_dogs': best_dogs_data})


@csrf_exempt
def search_doggos(request):

    found_dogs = []
    title_for_query = ''
    tag_for_query = ''
    query = False

    if request.method == 'POST':
        query = True
        title_for_query = request.POST.get("title", "")
        tag_for_query = request.POST.get("tag", "")
        found_dogs = dog_data_list[0:2]

    return render(request, 'search_doggos.html', {'found_dogs': found_dogs, 'query': query, 'title_for_query': title_for_query, 'tag_for_query': tag_for_query})
