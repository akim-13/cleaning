from .forms import FillOutForm, CustomUserCreationForm, CustomAuthenticationForm, LocationForm, ZoneFormSet
from .models import Location, User, Zone, Mark, Comment
from .decorators import groups_required
from django.http import Http404, JsonResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.dateparse import parse_date
from django.template.loader import render_to_string
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db.models import Q
from datetime import datetime, timedelta
from .utils import get_summary_data
from weasyprint import HTML
import redis, pytz, base64

redis_client = redis.Redis(host='redis', port=6379, db=0)
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


def get_form_data_row_by_row(data, row_num):
    form_data = {}
    for key, values in data.items():
        match key:
            case 'csrfmiddlewaretoken':
                form_data['csrfmiddlewaretoken'] = values[0]

            case 'submission_timestamp':
                form_data['submission_timestamp'] = values[0]

            case 'creation_timestamps[]':
                form_data['creation_timestamp'] = values[row_num]

            case 'zones[]':
                form_data['zone'] = values[row_num]

            case 'marks[]':
                form_data['mark'] = values[row_num]

            case 'approvals[]':
                form_data['is_approved'] = values[row_num]

            case 'customer_comments[]':
                form_data['customer_comment'] = values[row_num]

            case 'contractor_comments[]':
                form_data['contractor_comment'] = values[row_num]

    return form_data


def save_form_data(request, location):
    data = dict(request.POST)

    no_new_rows_added = data.get('zones[]') is None
    if no_new_rows_added:
        return None
        
    num_of_rows = len(data['zones[]'])
    for row_num in range(num_of_rows):
        row_form_data = get_form_data_row_by_row(data, row_num)
        form = FillOutForm(row_form_data, location=location)

        if form.is_valid():
            form.save(user=request.user)

            is_last_iteration = row_num == num_of_rows - 1
            if is_last_iteration:
                redis_client.set(f'submission_successful_in_{location}', 'true')
                # NOTE: The form is not needed, since we will get redirected now.
                return None
        else:
            redis_client.set(f'submission_successful_in_{location}', 'false')
            return form


# TODO: Untested! Especially the form submission part. Write thorough tests.
@groups_required('manager_customer', 'manager_contractor')
@login_required
def fill_out(request, location):
    if not Location.objects.filter(name=location).exists():
        raise Http404('Локация не найдена')

    form_data_saved_successfully = (redis_client.get(f'submission_successful_in_{location}') is not None) and (redis_client.get(f'submission_successful_in_{location}').decode('utf-8') == 'true')

    # a) Form is submitted.
    if request.method == 'POST':
        form = save_form_data(request, location)
        form_data_saved_successfully = redis_client.get(f'submission_successful_in_{location}').decode('utf-8') == 'true'

        # a.1) Form is valid; redirect to make a GET request.
        if form_data_saved_successfully:
            return redirect('fill_out', location=location)

        # a.2) Form is invalid; insert form errors via AJAX.
        request_is_ajax = request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'
        if request_is_ajax:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            }, status=400)

        # a.3) Invalid form and non-AJAX request. Should NEVER happen!!
        # TODO: Implement actual logging.
        print('ERROR\n'*5)
        print('How did you even get here? Use AJAX!!')
        print('form.errors:', form.errors)

    # b) GET request from "a.1)".
    elif form_data_saved_successfully:
        form = FillOutForm(location=location)

    # c) General GET request.
    else:
        # Do not render the page if there are multiple active users.
        # Instead, fetch the data from an active user via WebSockets (see `FillOutConsumer`).
        multiple_active_users_are_present = redis_client.scard(f'active_users_in_{location}') > 1
        if multiple_active_users_are_present:
            return render(request, 'main/fill_out.html', {
                'multiple_active_users_are_present': True,
                'location': location
            })

        redis_client.set(f'submission_successful_in_{location}', 'unknown')
        form = FillOutForm(location=location)


    groups_of_rows = generate_groups_of_rows(location)

    context = {
        'groups_of_rows': groups_of_rows,
        'form': form,
        'location': location,
    }

    submission_successful = redis_client.get(f'submission_successful_in_{location}').decode('utf-8')
    if submission_successful == 'true':
        channel_layer = get_channel_layer()
        page_contents_after_submission = render_to_string('main/fill_out.html', context)

        async_to_sync(channel_layer.group_send)(
            encode_location_name(location), {
                'type': 'send_page_contents_after_submission',
                'page_contents_after_submission': page_contents_after_submission,
            }
        )

    return render(request, 'main/fill_out.html', context)


def generate_groups_of_rows(location):
    # 1. Get all entries for the location from today.
    # 2. Find the earliest entry A by creation_datetime.
    # 3. Find all entries B that have the same submission_datetime as A.
    # 4. Generate rows for each entry (rows1).
    # 5. Generate formatted time periods - from creation_datetime to submission_datetime, both of A.
    # 6. Filter out all entries A and B.
    # 7. Repeat steps 2-6 for each time period.
    #
    # groups_of_rows = {'time_period1': [ rows1 ], 
    #                   'time_period2': [ rows2 ], 
    #                   'time_period3': [ rows3 ]...}

    groups_of_rows = {}

    timezone = pytz.timezone(Location.objects.get(name=location).timezone)
    now = timezone.localize(datetime.now())
    location_today_filter = Q(location__name=location, creation_datetime__date=now.date())
    todays_marks = Mark.objects.filter(location_today_filter).order_by('creation_datetime')
    todays_comments = Comment.objects.filter(location_today_filter).order_by('creation_datetime')
    
    while todays_marks:
        earliest_mark = todays_marks[0]
        earliest_submission_datetime = earliest_mark.submission_datetime
        same_time_period_marks = todays_marks.filter(submission_datetime=earliest_submission_datetime)
        same_time_period_comments = todays_comments.filter(submission_datetime=earliest_submission_datetime)

        same_time_period_rows = []
        for mark in same_time_period_marks:

            customer_comment, contractor_comment = '', ''
            try:
                # NOTE: If `customer_comment` doesn't exist, `contractor_comment` shouldn't exist either.
                customer_comment = todays_comments.get(creation_datetime=mark.creation_datetime, is_made_by_customer_not_contractor=True).comment
                # NOTE: If `contractor_comment` raises an exception, the value of `customer_comment` is preserved.
                contractor_comment = todays_comments.get(creation_datetime=mark.creation_datetime, is_made_by_customer_not_contractor=False).comment
            except Comment.DoesNotExist:
                pass
            except Comment.MultipleObjectsReturned:
                raise Exception('Multiple comments cannot have the same creation_datetime')

            row = {
                'zone': mark.zone.name,
                'mark': mark.mark,
                'approval': 'Да' if mark.is_approved else 'Нет',
                'customer_comment': customer_comment,
                'contractor_comment': contractor_comment
            }

            if row not in same_time_period_rows:
                same_time_period_rows.append(row)

        time_format = '%H:%M'
        time_period_start = earliest_mark.creation_datetime.astimezone(timezone).strftime(time_format)
        time_period_end = earliest_submission_datetime.astimezone(timezone).strftime(time_format)
        formatted_time_period = f'{time_period_start} - {time_period_end}'

        # NOTE: Weird edge case: if there are multiple submissions within one minute,
        # the second submission overwrites the first one, because they both have
        # the same time period (key). Fixed by adding a counter to duplicates.
        i = 1
        while formatted_time_period in groups_of_rows:
            formatted_time_period = f'{time_period_start} - {time_period_end} ({i})'
            i += 1

        groups_of_rows[formatted_time_period] = same_time_period_rows

        remove_processed_entries_filter = Q(submission_datetime__gt=earliest_submission_datetime)
        todays_comments = todays_comments.filter(remove_processed_entries_filter)
        todays_marks = todays_marks.filter(remove_processed_entries_filter)

    return groups_of_rows



def encode_location_name(location_name):
    encoded_location_name = base64.urlsafe_b64encode(location_name.encode('utf-8')).decode('utf-8')
    # Remove any '=' padding characters.
    encoded_location_name = encoded_location_name.rstrip('=')

    if len(encoded_location_name) >= 100:
        raise Exception('Location name is too long')

    return encoded_location_name
    

@groups_required('representative_customer', 'representative_contractor')
@login_required
def summary(request, location):
    # Use the utility function to get context data
    context = get_summary_data(request, location)

    return render(request, 'main/summary.html', {
        'location': context['location'],
        'zones_average_marks': context['zones_average_marks'],
        'total_average_mark': context['total_average_mark'],
        'start_date': context['start_date'].strftime('%Y-%m-%d') if context['start_date'] else '',
        'end_date': context['end_date'].strftime('%Y-%m-%d') if context['end_date'] else '',
        'groups_of_rows': context['groups_of_rows']
    })


@groups_required('representative_customer', 'representative_contractor')
@login_required
def summary_pdf(request, location):
    # Use the utility function to get context data
    context = get_summary_data(request, location)

    html_string = render_to_string('main/summary.html', {
        'location': context['location'],
        'zones_average_marks': context['zones_average_marks'],
        'total_average_mark': context['total_average_mark'],
        'start_date': context['start_date'].strftime('%Y-%m-%d') if context['start_date'] else '',
        'end_date': context['end_date'].strftime('%Y-%m-%d') if context['end_date'] else '',
        'groups_of_rows': context['groups_of_rows']
    })

    # Create a PDF from the HTML string
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="summary_{context["location"].name}.pdf"'

    # Generate PDF
    HTML(string=html_string).write_pdf(response)

    return response


@login_required
def configurator(request):
    if request.method == 'POST':
        location_form = LocationForm(request.POST)

        if location_form.is_valid():
            location = location_form.save()

            zones = request.POST.getlist('zones[]')
            for zone_name in zones:
                Zone.objects.create(location=location, name=zone_name)
            return redirect('main')

    else:
        location_form = LocationForm()

    return render(request, 'main/configurator.html', {
        'location_form': location_form,
    })
