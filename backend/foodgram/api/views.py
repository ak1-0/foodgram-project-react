from django.shortcuts import render, HttpResponse
from djoser.views import UserViewSet

def index(request):
    return HttpResponse('index')

class CustomUserViewSet(UserViewSet):
    pass
