from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import User, Mark, Comment, Zone, Location

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2')
        labels = {
            'username': ('Логин'),
            'password1': ('Пароль'),
            'password2': ('Подтвердите пароль'),
        }


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = ('username',)
        labels = {
            'username': ('Логин'),
        }


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'
    
    class Meta:
        model = User
        fields = ('username', 'password')


class MarkForm(forms.ModelForm):
    class Meta:
        model = Mark
        fields = ['zone', 'mark', 'is_approved']


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        # NOTE: Ommitting the `photo` field for now.
        fields = ['zone', 'comment', 'is_made_by_customer_not_contractor']


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['location_name', 'mark_range_min', 'mark_range_max']


class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['zone_name', 'location']
