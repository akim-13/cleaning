from django.contrib import admin
from .models import Cell, Location, Zone, User

admin.site.register(Cell)
admin.site.register(Location)
admin.site.register(Zone)
admin.site.register(User)