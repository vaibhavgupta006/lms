from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from .forms import UserRegistrationForm, UserLoginFrom
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView


class SignupView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'authentication/signup.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard:home'))
        else:
            return super().get(request, *args, **kwargs)


class MyLoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = UserLoginFrom

    def get_success_url(self, *args, **kwargs):
        return reverse_lazy('dashboard:home')

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard:home'))
        else:
            return super().get(request, *args, **kwargs)


def HomeView(request):
    return render(request, 'authentication/home.html')
