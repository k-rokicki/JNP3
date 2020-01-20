from django.urls import path

from . import views


urlpatterns = [
    path('', views.single_doggo, name='single'),
    path('<int:dog_id>', views.single_doggo, name='single_with_id'),
    path('random', views.random_redirect, name='random_redirect'),
    path('search', views.search_doggos, name='search'),
    path('top', views.top_doggos, name='top'),
    path('rate/<int:dog_id>', views.rate_doggo, name='rate'),
    path('upload', views.upload_doggo, name='upload'),
]
