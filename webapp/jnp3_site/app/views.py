from django.shortcuts import render, HttpResponse


def main_page(request):
    return render(request, 'main_page.html')

