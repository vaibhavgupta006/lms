from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.urls import reverse

# Create your views here.


def HomeView(request):
    return HttpResponseRedirect(reverse('authentication:login'))
