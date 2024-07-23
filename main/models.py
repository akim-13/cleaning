from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

# TODO: Add editable=False to all fields that should be set automatically.
# E.g. user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
# Currently, these are not set for debugging purposes.

class Location(models.Model):
    location_name = models.CharField(max_length=255)
    mark_range_min = models.SmallIntegerField(default=0)
    mark_range_max = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.location_name

class CustomUserManager(BaseUserManager):

    def create_user(self, username, password, **extra_fields): 
        if not username:
            raise ValueError('The Username field must be set')
        if not password:
            raise ValueError('The Password field must be set')
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
        return self.create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255, unique=True)
    password = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['password'] 
    
    # These settings are needed for avoiding conflicts with varible names 
    # and relations between default django settings and the db table
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        help_text=('The groups this user belongs to.'),
        verbose_name=('groups'),
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_permissions_set',
        blank=True,
        help_text=('Specific permissions for user.'),
        verbose_name=('user permissions'),
    )
    
    # For connecting to db table.
    class Meta:
        db_table = 'users'
    
    def __str__(self):
        return self.username


class Zone(models.Model):
    # Relationships.
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='zones', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, related_name='zones', null=True, blank=True)

    zone_name = models.CharField(max_length=255)

    def __str__(self):
        return self.zone_name


class Mark(models.Model):
    # Relationships.
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='marks')
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False, related_name='marks')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='marks')

    # TODO: Use mark_range_min and mark_range_max from Location (seems hard to implement atm).
    MARK_CHOICES = [(i, i) for i in range(0, 6)]
    mark = models.SmallIntegerField(choices=MARK_CHOICES)
    is_approved = models.BooleanField(default=False)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        display_string = f'[{self.location}] {self.zone}: {self.mark}'
        
        if self.is_approved:
            return display_string + ' (✔)'
        else:
            return display_string + ' (❌)'


class Comment(models.Model):
    # Relationships.
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False, related_name='comments')
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True, related_name='comments')

    is_made_by_customer_not_contractor = models.BooleanField()
    comment = models.TextField(blank=True)
    allocated_time = models.TimeField(default=timezone.now)

    photo = models.ImageField(upload_to='./attachments/', null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)

    def __str__(self):
        display_string = f'[{self.location}] {self.zone}: '
        if self.is_made_by_customer_not_contractor:
            return display_string + f'Customer: "{self.comment}"'
        else:
            return display_string + f'Contractor: "{self.comment}"'