from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def get_tweets(request, config_id):
    return HttpResponse("This is a response!")
