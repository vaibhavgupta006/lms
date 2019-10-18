from django.urls import path
from django.conf.urls import url
from .views import SignupView, MyLoginView, HomeView
from django.contrib.auth import views as auth_views

app_name = 'authentication'
urlpatterns = [
    path('', HomeView, name='home'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', MyLoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

]
