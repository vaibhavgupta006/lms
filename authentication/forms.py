from django import forms
from .models import User
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm


class UserRegistrationForm(UserCreationForm):

    email = forms.CharField(
        label='Email',
        required=True,
    )
    last_name = forms.CharField(
        label='Last name',
        required=True,
    )
    first_name = forms.CharField(
        label='First name',
        required=True,
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.TextInput(
            attrs={'type': "password"}
        ),
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.TextInput(
            attrs={'type': "password"}
        ),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "email",
        ]


class UserLoginFrom(AuthenticationForm):
    username = forms.CharField(label='Email',)

    password = forms.CharField(
        label='Password',
        widget=forms.TextInput(
            attrs={"type": "password"}
        )
    )
