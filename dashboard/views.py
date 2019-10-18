from django.shortcuts import render
from django.views.generic import DetailView
from authentication.models import User
# Create your views here.


class HomeView(DetailView):
    template_name = 'dashboard/home.html'

    def get_object(self, queryset=None):
        return User.objects.get(id=self.request.user.id)
