from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import User
from django.utils.translation import gettext_lazy as _

# Needed for password hashing.
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')  
        labels = {
            'username': _('Username'),  
            'password1': _('Password'),
            'password2': _('Confirm password'),  
        }

# Needed for changing user settings such as admin page access.
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username',)
        labels = {
            'username': _('Username'),
        }

# Verification by using username and password in the db.
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')
        labels = {
            'username': _('Username'),
            'password': _('Password'),
        }