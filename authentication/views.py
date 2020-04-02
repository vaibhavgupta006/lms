from django.shortcuts import render
from django.urls import reverse_lazy, reverse
from .forms import UserRegistrationForm, UserLoginFrom
from django.views.generic import CreateView
from django.http import HttpResponseRedirect
from django.contrib.auth.views import LoginView
from django.contrib.auth import login, authenticate


class SignupView(CreateView):
    form_class = UserRegistrationForm
    template_name = 'authentication/signup.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('dashboard:home'))
        else:
            return super().get(request, *args, **kwargs)

    def form_valid(self, form, *args, **kwargs):
        super().form_valid(form, *args, **kwargs)
        email = form.cleaned_data.get('email')
        password = form.cleaned_data.get('password1')
        user = authenticate(email=email, password=password)
        login(self.request, user)
        return HttpResponseRedirect(reverse_lazy('dashboard:home'))


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
    return HttpResponseRedirect(reverse('authentication:login'))
