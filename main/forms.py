from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django import forms
from .models import User, Location, Zone 

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
        
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs) 
        # Exclude the 'admin_account' role from the choices 
        self.fields['role'].choices = [
            (key, value) for key, value in self.fields['role'].choices if key != 'admin_account' 
            ]

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

class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['location_name', 'mark_range_min', 'mark_range_max']
        labels = {
            'location_name': 'Название объекта',
            'mark_range_min': 'Минимальная оценка',
            'mark_range_max': 'Максимальная оценка',
        }
        widgets = {
            'mark_range_min': forms.NumberInput(attrs={'min': 0, 'max': 100}),
            'mark_range_max': forms.NumberInput(attrs={'min': 0, 'max': 100}),
        }

class ZoneForm(forms.ModelForm):
    class Meta:
        model = Zone
        fields = ['zone_name']
        labels = {
            'zone_name': 'Название зоны',
        }

ZoneFormSet = forms.inlineformset_factory(Location, Zone, form=ZoneForm, extra=1, can_delete=True)