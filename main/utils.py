from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_date
from datetime import timedelta
from .models import Location, Mark, Comment, Zone
import pytz

def get_summary_data(request, location):
    location = get_object_or_404(Location, name=location)

    # Extract start date and end date from the GET request
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Parse the start date and end date to date objects
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None

    zones_average_marks = {}
    total_average_mark = 0
    groups_of_rows = {}

    # Check if the dates are valid
    if start_date and end_date:
        if start_date > end_date:
            messages.info(request, "Выберите период правильно: начало периода не может быть позже конца.")
        else:
            # Ensure end date includes the entire day
            end_date = end_date + timedelta(days=1)

            # Filter marks by location and date range
            marks = Mark.objects.filter(
                location=location,
                creation_datetime__range=[start_date, end_date]
            ).order_by('creation_datetime')

            comments = Comment.objects.filter(
                location=location,
                creation_datetime__range=[start_date, end_date]
            ).order_by('creation_datetime')

            # Get all the zones for the location
            zone_names = Zone.objects.filter(location=location).values_list('name', flat=True)
            
            # Calculate the average marks for each zone
            for zone_name in zone_names:
                zone_marks = marks.filter(zone__name=zone_name)
                zone_average_mark = sum(mark.mark for mark in zone_marks) / len(zone_marks) if len(zone_marks) > 0 else 0
                zones_average_marks[zone_name] = zone_average_mark

            # Calculate the total average mark
            if zones_average_marks:
                total_average_mark = sum(zones_average_marks.values()) / len(zones_average_marks)

            # Group marks and comments by time period
            while marks.exists():
                earliest_mark = marks.first()
                earliest_submission_datetime = earliest_mark.submission_datetime
                same_time_period_marks = marks.filter(submission_datetime=earliest_submission_datetime)
                same_time_period_comments = comments.filter(submission_datetime=earliest_submission_datetime)

                same_time_period_rows = []
                for mark in same_time_period_marks:
                    customer_comment = ''
                    contractor_comment = ''
                    try:
                        customer_comment = same_time_period_comments.get(
                            creation_datetime=mark.creation_datetime, is_made_by_customer_not_contractor=True
                        ).comment
                        contractor_comment = same_time_period_comments.get(
                            creation_datetime=mark.creation_datetime, is_made_by_customer_not_contractor=False
                        ).comment
                    except Comment.DoesNotExist:
                        pass
                    except Comment.MultipleObjectsReturned:
                        raise Exception('Несколько комментариев не могут существовать')

                    row = {
                        'zone': mark.zone.name,
                        'mark': mark.mark,
                        'customer_comment': customer_comment,
                        'contractor_comment': contractor_comment
                    }

                    if row not in same_time_period_rows:
                        same_time_period_rows.append(row)

                # Format the time period and date
                time_format = '%H:%M'
                date_format = '%Y-%m-%d'
                time_zone = pytz.timezone(earliest_mark.location.timezone)  # Fetch timezone
                date_display = earliest_mark.creation_datetime.astimezone(time_zone).strftime(date_format)
                time_period_start = earliest_mark.creation_datetime.astimezone(time_zone).strftime(time_format)
                time_period_end = earliest_submission_datetime.astimezone(time_zone).strftime(time_format)
                formatted_time_period = f'{time_period_start} - {time_period_end}'

                # Handle duplicates in the formatted time period
                i = 1
                while (date_display, formatted_time_period) in groups_of_rows:
                    formatted_time_period = f'{time_period_start} - {time_period_end} ({i})'
                    i += 1

                groups_of_rows[(date_display, formatted_time_period)] = same_time_period_rows

                # Remove processed entries
                marks = marks.filter(submission_datetime__gt=earliest_submission_datetime)
                comments = comments.filter(submission_datetime__gt=earliest_submission_datetime)
    else:
        messages.info(request, "Пожалуйста, выберите начало и конец периода.")

    # Return data in a dictionary
    return {
        'location': location,
        'zones_average_marks': zones_average_marks,
        'total_average_mark': total_average_mark,
        'start_date': start_date,
        'end_date': end_date,
        'groups_of_rows': groups_of_rows,
    }
