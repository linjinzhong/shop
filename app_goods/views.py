from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, Http404


# Create your views here.


def index(request):
    AA = {
        "a": "abc",
        "b": "sss",
        "c": "ssss",
        "ss": "sssssssss",
        "sss": "sssssssssssssssssssssssssssssssssssssss",
    }
    return render(request, "index.html", AA)
