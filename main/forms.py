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


class FillOutForm(forms.Form):
    # TODO: Use zones for the specific location.
    zone = forms.ModelChoiceField(queryset=Zone.objects.all())
    mark = forms.ChoiceField(choices=Mark.MARK_CHOICES)
    is_approved = forms.BooleanField()
    customer_comment = forms.CharField()
    contractor_comment = forms.CharField()

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

    def save(self, user, location):
        zone = self.cleaned_data['zone']

        mark = Mark(
            zone=zone,
            user=user,
            location=Location.objects.get(location_name=location),
            mark=self.cleaned_data['mark'],
            is_approved=self.cleaned_data['is_approved']
        )
        mark.save()

        if self.cleaned_data['customer_comment']:
            customer_comment = Comment(
                zone=zone,
                user=user,
                location=Location.objects.get(location_name=location),
                comment=self.cleaned_data['customer_comment'],
                is_made_by_customer_not_contractor=True
            )
            customer_comment.save()

        if self.cleaned_data['contractor_comment']:
            contractor_comment = Comment(
                zone=zone,
                user=user,
                location=Location.objects.get(location_name=location),
                comment=self.cleaned_data['contractor_comment'],
                is_made_by_customer_not_contractor=False
            )
            contractor_comment.save()



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
