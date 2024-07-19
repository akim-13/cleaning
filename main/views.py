from .models import Cell, Location, User, Zone
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm


def login_view(request):
    # if smth was filled and submitted
    if request.method == 'POST':
        # related to forms, used for validating login credentials
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # checks if there exists user
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main')
    else:
        # create a new blank (for get, when u load page or above data is incorrect)
        form = CustomAuthenticationForm()
    return render(request, 'main/login.html', {'form': form})

def register_view(request):
    # almost simmilar to login
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('main')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})

def fill_out(request, location):
    return render(request, 'main/fill_out.html')

def main(request):
    return render(request, 'main/main.html')

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