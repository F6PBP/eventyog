from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from modules.main.models import *

def main(request: HttpRequest) -> HttpResponse:
    return render(request, 'yogevent.html')