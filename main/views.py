from django.shortcuts import render
from .models import Cell, Location, Zone, User


def login(request):
    return render(request, 'main/login.html')


def register(request):
    return render(request, 'main/register.html')


def fill_out(request, location):
    return render(request, 'main/fill_out.html')


def summary(request, location):
    # TODO: Get everything from the database.
    # 1. Get all the zones for the location.
    # 2. For each zone, get all its cells and calculate the average mark.
    # 3. Calculate the total average mark for the location: sum(average marks) / count(zones).
    zones = None
    zones_average_marks = None 
    total_average_mark = 4.8
    context = { 
        'zones': zones,
        'zones_average_marks': zones_average_marks,
        'total_average_mark': total_average_mark
    }
    return render(request, 'main/summary.html', context)


def configure(request, location):
    return render(request, 'main/configure.html')