from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _ 

class CustomPasswordValidator:
    def validate (self, password, user=None):
        if not any(char.islower() for char in password):
            raise ValidationError(_('Пароль должен содержать как минимум одну маленькую букву.'))
        if not any(char.islower() for char in password):
            raise ValidationError(_('Пароль должен содержать как минимум одну заглавную букву.'))
        if not any(char.isdigit() for char in password):
            raise ValidationError(_('Пароль должен содержать как минимум одну цифру.'))
        if len(password) < 8:
            raise ValidationError(_('Пароль должен содержать как минимум 8 символов'))
        
    def get_help_text(self):
        return _('Пароль должен содержать маленькую букву, заглавную букву и цифру.')
