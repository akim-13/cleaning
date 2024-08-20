from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from .models import User, Mark, Comment, Zone, Location
from datetime import datetime, timezone
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


class FillOutForm(forms.Form):
    # NOTE: The `zone` field is set in the `__init__` method.
    zone = forms.ModelChoiceField(queryset=Zone.objects.none())
    mark = forms.ChoiceField(choices=Mark.MARK_CHOICES)
    is_approved = forms.BooleanField()
    customer_comment = forms.CharField(required=False)
    contractor_comment = forms.CharField(required=False)

    # Hidden fields.
    creation_timestamp = forms.IntegerField()
    submission_timestamp = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        self.location = kwargs.pop('location', None)
        if self.location is None:
            raise ValueError('Location is required when creating a FillOutForm')

        super().__init__(*args, **kwargs)
        self.fields['zone'].queryset = Zone.objects.filter(location__name=self.location)


    def clean(self):
        cleaned_data = super().clean()
        zone = cleaned_data.get('zone')
        mark = cleaned_data.get('mark')
        is_approved = cleaned_data.get('is_approved')

        if zone is None:
            raise forms.ValidationError('Zone is required')
        if mark is None:
            raise forms.ValidationError('Mark is required')
        if not is_approved:
            raise forms.ValidationError('Approval is required')

        return cleaned_data


    def save(self, user):
        location = Location.objects.get(name=self.location)
        zone = Zone.objects.get(name=self.cleaned_data['zone'], location=location)

        creation_timestamp = int(self.cleaned_data['creation_timestamp'])
        creation_datetime = datetime.fromtimestamp(creation_timestamp, timezone.utc)
        submission_timestamp = int(self.cleaned_data['submission_timestamp'])
        submission_datetime = datetime.fromtimestamp(submission_timestamp, timezone.utc)

        mark = Mark(
            zone=zone,
            user=user,
            location=location,
            mark=self.cleaned_data['mark'],
            is_approved=self.cleaned_data['is_approved'],
            creation_datetime=creation_datetime,
            submission_datetime=submission_datetime
        )
        mark.save()

        if self.cleaned_data['customer_comment']:
            customer_comment = Comment(
                zone=zone,
                user=user,
                location=location,
                comment=self.cleaned_data['customer_comment'],
                is_made_by_customer_not_contractor=True,
                creation_datetime=creation_datetime,
                submission_datetime=submission_datetime
            )
            customer_comment.save()

        if self.cleaned_data['contractor_comment']:
            contractor_comment = Comment(
                zone=zone,
                user=user,
                location=location,
                comment=self.cleaned_data['contractor_comment'],
                is_made_by_customer_not_contractor=False,
                creation_datetime=creation_datetime,
                submission_datetime=submission_datetime
            )
            contractor_comment.save()


class LocationForm(forms.ModelForm):
    class Meta:
        model = Location
        fields = ['name', 'mark_range_min', 'mark_range_max']
        labels = {
            'name': 'Название объекта',
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

        fields = ['name']
        labels = {
            'name': 'Название зоны',
        }

ZoneFormSet = forms.inlineformset_factory(Location, Zone, form=ZoneForm, extra=1, can_delete=True)