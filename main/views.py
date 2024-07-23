from .models import Location, User, Zone, Mark,Comment
from django.shortcuts import render, redirect
from django.db.models import Q
from django.contrib.auth import login, authenticate
from .forms import CustomUserCreationForm, CustomAuthenticationForm

def login_view(request):
    # if smth was filled and submitted, basically checks if smth was posted 
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
    # almost similar to login
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
    # Get all the zones for the location.
    zone_names = Zone.objects.filter(location__location_name=location).values_list('zone_name', flat=True)
    rows = []

    # TODO: Does not account for multiple marks/comments per zone, i.e. time.
    for zone in zone_names:
        location_zone_filter = Q(location__location_name=location, zone__zone_name=zone)
        marks = list(Mark.objects.filter(location_zone_filter))
        customer_comments = list(Comment.objects.filter(location_zone_filter, is_made_by_customer_not_contractor=True))
        contractor_comments = list(Comment.objects.filter(location_zone_filter, is_made_by_customer_not_contractor=False))

        row = {
            'zone': zone,
            'mark': marks[0].mark if marks else 'Н/Д',
            'approval': '✔' if (marks and marks[0].is_approved) else '❌',
            'customer_comment': customer_comments[0].comment if customer_comments else '',
            'contractor_comment': contractor_comments[0].comment if contractor_comments else ''
        }
        rows.append(row)

        # Remove the first element from the lists.
        marks = marks[1:]
        customer_comments = customer_comments[1:]
        contractor_comments = contractor_comments[1:]

    context = {
        'rows': rows
    }

    return render(request, 'main/fill_out.html', context)


def main(request):
    return render(request, 'main/main.html')


def summary(request, location):
    # Get all the zones for the location.
    zone_names = Zone.objects.filter(location__location_name=location).values_list('zone_name', flat=True)

    # For each zone, get all its cells and calculate the average mark.
    zones_average_marks = {}
    for zone in zone_names:
        marks = Mark.objects.filter(location__location_name=location, zone__zone_name=zone)
        zone_average_mark = sum(mark.mark for mark in marks) / len(marks) if len(marks) > 0 else 0
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