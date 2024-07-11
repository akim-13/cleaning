from django.db import models
#from django.contrib.auth.models import AbstractUser
from django.utils import timezone

#class User(AbstractUser):
    #pass

class Location(models.Model):
    location_name = models.CharField(max_length=255)

class Zone(models.Model):
    zone_name = models.CharField(max_length=255)

class Criterion(models.Model):
    criterion_name = models.CharField(max_length=255)
    mark_range_min = models.SmallIntegerField(default=0)
    mark_range_max = models.SmallIntegerField(default=5)

class Cell(models.Model):
    mark = models.SmallIntegerField()
    confirmation = models.BooleanField()
    customer_comment = models.TextField()
    customer_comment_time = models.DateTimeField(default=timezone.now)
    customer_comment_photo = models.ImageField()
    contractor_comment = models.TextField()
    contractor_comment_time = models.DateTimeField(default=timezone.now)
    contractor_comment_photo = models.ImageField()
