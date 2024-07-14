from django.contrib import admin
from .models import Cell, Location, Zone, Criterion, User

# FIXME: Most of these don't work on the admin website 
# when trying to view or add e.g. a Cell or a Zone.
admin.site.register(Cell)
admin.site.register(Location)
admin.site.register(Zone)
admin.site.register(Criterion)
admin.site.register(User)