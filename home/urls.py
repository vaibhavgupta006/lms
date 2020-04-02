from django.urls import path
from django.conf.urls import url
from .views import HomeView

app_name = 'home'
urlpatterns = [
    path('', HomeView, name='home')
]
