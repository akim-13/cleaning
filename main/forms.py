from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User
from django.utils.translation import gettext_lazy as _

# needed for hashing password
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')  
        labels = {
            'username': _('Username'),  
            'password1': _('Password'),
            'password2': _('Confirm password'),  
        }

class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username',)
        labels = {
            'username': _('Username'),
        }

class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        labels = {
            'username': _('Username'),
            'password': _('Password'),
        }