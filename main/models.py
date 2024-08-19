from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# TODO: Add editable=False to all fields that should be set automatically.
# E.g. user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
# Currently, these are not set for debugging purposes.

class Location(models.Model):
    name = models.CharField(verbose_name = 'Объект', max_length=255)
    timezone = models.CharField(max_length=255, default='Europe/Moscow')
    mark_range_min = models.SmallIntegerField(verbose_name = 'Минимальная оценка', default=0)
    mark_range_max = models.SmallIntegerField(verbose_name = 'Максимальная оценка', default=5)

    def __str__(self):
        return self.name

class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields): 
        if not username:
            raise ValueError('Логин должен быть заполнен')
        if not password:
            raise ValueError('Пароль должен быть заполнен')
        extra_fields.setdefault('is_active', False)
        user = self.model(username=username, **extra_fields)
        # Hashes the password before putting it in the db.
        user.set_password(password)
        user.save(using=self._db)
        return user

    # Extra settings for superusers, such as `is_staff`,
    # which allows the user to log into the admin pannel.
    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        # Superusers should be active by default
        extra_fields.setdefault('is_active', True)  
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    ROLES_CHOICES = [
        ('manager_contractor', 'Менеджер Исполнитель'),
        ('manager_customer', 'Менеджер Заказчик'),
        ('representative_customer', 'Руководитель Объекта'),
        ('representative_contractor', 'Руководитель Клининга'),
    ]
    
    username = models.CharField(verbose_name="Логин",max_length=255, unique=True)
    password = models.CharField(verbose_name="Пароль", max_length=255)
    is_active = models.BooleanField(verbose_name="Активен", default=True)
    is_staff = models.BooleanField(verbose_name="Админ", default=False)
    role = models.CharField(verbose_name = 'Роль', max_length=55, choices = ROLES_CHOICES, default = 'manager_customer')
    location = models.ManyToManyField(Location, verbose_name='Объекты', related_name='users', blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password'] 
    
    # These settings are needed for avoiding conflicts with varible names 
    # and relations between default django settings and the db table
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text=('Роли к которым принадлежит пользователь.'),
        verbose_name=('Роли'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text=('Специальные возможности пользователя.'),
        verbose_name=('Возможности пользователя'),
    )
    
    # For connecting to tne db table.
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Zone(models.Model):
    # Relations.
    created_by = models.ForeignKey(User, verbose_name="Создано", on_delete=models.PROTECT, related_name='zones', null=True, blank=True)
    location = models.ForeignKey(Location, verbose_name="Объект", on_delete=models.CASCADE, related_name='zones', null=True, blank=True)

    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Mark(models.Model):
    # Relations.
    zone = models.ForeignKey(Zone, verbose_name = 'Зона', on_delete=models.CASCADE, related_name='marks')
    user = models.ForeignKey(User, verbose_name = 'Пользователь', on_delete=models.PROTECT, null=True, blank=True, editable=False, related_name='marks')
    location = models.ForeignKey(Location, verbose_name = 'Объект', on_delete=models.CASCADE, null=True, blank=True, related_name='marks')

    # TODO: Use mark_range_min and mark_range_max from Location (seems hard to implement atm).
    MARK_CHOICES = [(i, i) for i in range(0, 6)]
    mark = models.SmallIntegerField(verbose_name = 'Оценка', choices=MARK_CHOICES)
    is_approved = models.BooleanField(verbose_name = 'Подтверждение', default=False)
    # NOTE: The default value is overridden in form's `save()` 
    # method to store the time when the form was created.
    creation_datetime = models.DateTimeField(default=timezone.now)
    submission_datetime = models.DateTimeField(verbose_name = 'Последние изменение', default=timezone.now)

    def __str__(self):
        display_string = f'[{self.location}] {self.zone}: {self.mark} '
        
        if self.is_approved:
            return display_string + '(✔)'
        else:
            return display_string + '(❌)'


class Comment(models.Model):
    # Relations.
    zone = models.ForeignKey(Zone, verbose_name = 'Зона', on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, verbose_name = 'Пользователь', on_delete=models.PROTECT, null=True, blank=True, editable=False, related_name='comments')
    location = models.ForeignKey(Location, verbose_name = 'Объект', on_delete=models.CASCADE, null=True, blank=True, related_name='comments')

    is_made_by_customer_not_contractor = models.BooleanField(verbose_name='Это сделано Заказчиком, а не Исполнителем')
    comment = models.TextField(verbose_name = 'Комментарий', blank=True)
    allocated_time = models.TimeField(verbose_name = 'Время', default=timezone.now)

    photo = models.ImageField(upload_to='./attachments/', verbose_name = 'Фото', null=True, blank=True)
    # NOTE: The default value is overridden in form's `save()` 
    # method to store the time when the form was created.
    creation_datetime = models.DateTimeField(default=timezone.now)
    submission_datetime = models.DateTimeField(verbose_name = 'Последение изменение',default=timezone.now)

    def __str__(self):
        display_string = f'[{self.location}] {self.zone}: '
        if self.is_made_by_customer_not_contractor:
            return display_string + f'Customer: "{self.comment}"'
        else:
            return display_string + f'Contractor: "{self.comment}"'
