from django.db import models
from django.utils import timezone

# TODO: Add editable=False to all fields that should be set automatically.
# E.g. user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
# Currently, these are not set for debugging purposes.

class Location(models.Model):
    location_name = models.CharField(max_length=255)

    def __str__(self):
        return self.location_name


class User(models.Model):
    # Relationships
    location = models.ManyToManyField(Location)

    username = models.CharField(max_length=255)
    password = models.CharField(max_length=255)
    role = models.CharField(max_length=255)

    def __str__(self):
        return self.username


class Zone(models.Model):
    # Relationships
    created_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name='zones_created', null=True, blank=True)
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
    # TODO: CASCADE or PROTECT for zone?
    zone = models.ForeignKey(Zone, on_delete=models.CASCADE)
    criterion = models.ForeignKey(Criterion, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True, blank=True, editable=False)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, null=True, blank=True)

    # TODO: Use mark_range_min and mark_range_max from Criterion (seems har to implement atm).
    MARK_CHOICES = [(i, i) for i in range(0, 6)]
    mark = models.SmallIntegerField(choices=MARK_CHOICES)
    confirmation = models.BooleanField()

    customer_comment = models.TextField(blank=True)
    customer_comment_time = models.TimeField(default=timezone.now)
    customer_comment_photo = models.ImageField(upload_to='./media/customer_photos/', null=True, blank=True)

    contractor_comment = models.TextField(blank=True)
    contractor_comment_time = models.TimeField(default=timezone.now)
    contractor_comment_photo = models.ImageField(upload_to='./media/contractor_photos/', null=True, blank=True)

    def __str__(self):
        return (self.criterion, self.zone)
