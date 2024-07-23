from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import User

# Needed for password hashing.
class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # Specify the required fields, otherwise there will
        # be too many of them such as email, last name, etc.
        fields = ('username',)
        
# Needed for changing user settings such as admin page access.
class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username',)

# Verification by using username and password in db.
class CustomAuthenticationForm(AuthenticationForm):
    class Meta:
        model = User
        fields = ('username', 'password')
