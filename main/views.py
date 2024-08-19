from django.contrib.auth.decorators import login_required
from .decorators import groups_required
from .models import Location, User, Zone, Mark, Comment
from .forms import CustomUserCreationForm, CustomAuthenticationForm, LocationForm, ZoneFormSet
from django.shortcuts import render, redirect
from django.http import Http404
from django.db.models import Q
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import Group

def login_view(request):
    # If something has been filled and submitted. 
    if request.method == 'POST':
        # Related to forms, used for validating login credentials.
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            # Check if the user exists.
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('main')
    else:
        # Create a new blank (for getting, when you
        # load the page or above data is incorrect).
        form = CustomAuthenticationForm()
    return render(request, 'main/login.html', {'form': form})


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            # Do not save the user yet
            user = form.save(commit=False) 
            # Ensure the user is inactive
            user.is_active = False  
            # Now save the user
            user.save()  
            # Important for saving ManyToMany relationships
            form.save_m2m()  
            role = form.cleaned_data.get('role')
            group = Group.objects.get(name=role)
            user.groups.add(group)
            return redirect('/')
    else:
        form = CustomUserCreationForm()
    return render(request, 'main/register.html', {'form': form})


@login_required
def main(request):
    return render(request, 'main/main.html')


@groups_required('manager_customer', 'manager_contractor')
@login_required
def fill_out(request, location):
    if not Location.objects.filter(location_name=location).exists():
        raise Http404('Локация не найдена')

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
            'approval': 'Да' if (marks and marks[0].is_approved) else 'Нет',
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


@groups_required('representative_customer', 'representative_contractor')
@login_required
def summary(request, location):
    if not Location.objects.filter(location_name=location).exists():
        raise Http404('Локация не найдена')

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


@groups_required ('representative_contractor')
@login_required
def configure(request):
    if request.method == 'POST':
        location_form = LocationForm (request.POST)
        zone_form = ZoneFormSet (request.POST)
        
        if location_form.is_valid() and zone_form.is_valid():
            location = location_form.save()
            zones = zone_form.save(commit=False)
            for zone in zones:
                zone.location = location 
                zone.save()
            return redirect('main/main.html')
        
    else:
        location_form = LocationForm()
        zone_form = ZoneFormSet()
    
    
    return render(request, 'main/configure.html', {
        'location_form': location_form,
        'zone_form': zone_form
    })
