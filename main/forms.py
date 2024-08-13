from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import User, Location

class CustomUserCreationForm(UserCreationForm):
    location = forms.ModelMultipleChoiceField(
        queryset = Location.objects.all(),  
        required = False,
        label = "Выберите объекты (не выбирать, если вы руководитель клин. компании)",
        widget = forms.CheckboxSelectMultiple
    )

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'password1', 'password2', 'role', 'location')
        labels = {
            'username': 'Логин',
            'password1': 'Пароль',
            'password2': 'Подтвердите пароль',
            'role': 'Выберите вашу роль',
            'location': 'Выберите объект ',
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
