from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.conf import settings
from django.urls import reverse


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(blank=False, null=False, unique=True)
    REQUIRED_FIELDS = ['username']
    first_name = models.CharField(max_length=20)
    last_name = models.CharField(max_length=20)
    username = models.CharField(
        max_length=50, null=True, blank=True, unique=False
    )

    def get_absolute_url(self):
        return reverse('dashboard:home')
