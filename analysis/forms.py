from django import forms
from .models import User

from django.contrib.auth.forms import UserCreationForm
class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['department','role', "username","first_name", "last_name", "email",  "password1", "password2"]

    def save(self, commit=True):
        user = super().save(commit=False) 
        if commit:
            user.save()
        return user  