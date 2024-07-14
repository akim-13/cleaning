#from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class Location(models.Model):
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return self.location_name


class User(models.Model):
    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)
    # TODO: Not ForeignKey if many-to-many
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)


class Zone(models.Model):
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='zones_created', null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    zone_name = models.CharField(max_length=255)

    def __str__(self):
        return self.zone_name


class Criterion(models.Model):
    # Relationships
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    criterion_name = models.CharField(max_length=255)
    mark_range_min = models.SmallIntegerField(default=0)
    mark_range_max = models.SmallIntegerField(default=5)

    def __str__(self):
        return self.criterion_name


class Cell(models.Model):
    # Relationships
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    mark = models.SmallIntegerField()
    confirmation = models.BooleanField()

    customer_comment = models.TextField()
    customer_comment_time = models.DateTimeField(default=timezone.now)
    customer_comment_photo = models.ImageField(upload_to='./media/customer_photos/', null=True, blank=True)

    contractor_comment = models.TextField()
    contractor_comment_time = models.DateTimeField(default=timezone.now)
    contractor_comment_photo = models.ImageField(upload_to='./media/contractor_photos/', null=True, blank=True)

    def __str__(self):
        return (self.zone, self.criterion)
