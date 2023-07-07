from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404

# Create your views here.


def index(request):
    return HttpResponse({"res": "status"})
