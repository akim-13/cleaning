from django.shortcuts import render
from .models import Cell, Location, Zone, User


def login(request):
    return render(request, 'main/login.html')


def register(request):
    return render(request, 'main/register.html')


def fill_out(request, location):
    return render(request, 'main/fill_out.html')


def summary(request, location):
    print(location)
    # Get all the zones for the location.
    zone_names = Zone.objects.filter(location__location_name=location).values_list('zone_name', flat=True)

    # For each zone, get all its cells and calculate the average mark.
    zones_average_marks = {}
    for zone in zone_names:
        cells = Cell.objects.filter(location__location_name=location, zone__zone_name=zone)
        zone_average_mark = sum(cell.mark for cell in cells) / len(cells) if len(cells) > 0 else 0
        zones_average_marks[zone] = zone_average_mark

    total_average_mark = sum(zones_average_marks.values()) / len(zones_average_marks) if len(zones_average_marks) > 0 else 0

    context = { 
        'location': location,
        'zones_average_marks': zones_average_marks,
        'total_average_mark': total_average_mark
    }

    return render(request, 'main/summary.html', context)


def configure(request, location):
    return render(request, 'main/configure.html')