from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils.dateparse import parse_date
from datetime import timedelta
from .models import Location, Mark, Comment, Zone
import pytz

def get_summary_data(request, location):
    location = get_object_or_404(Location, name=location)
    
    has_non_blank_sectors = False

    # Extract start and end dates
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    start_date = parse_date(start_date) if start_date else None
    end_date = parse_date(end_date) if end_date else None

    zones_average_marks = {}
    total_average_mark = 0
    groups_of_rows = {}

    if start_date and end_date:
        if start_date > end_date:
            messages.info(request, "Выберите период правильно: начало периода не может быть позже конца.")
        else:
            end_date = end_date + timedelta(days=1)
            marks = Mark.objects.filter(location=location, creation_datetime__range=[start_date, end_date])
            comments = Comment.objects.filter(location=location, creation_datetime__range=[start_date, end_date])

            zones = Zone.objects.filter(location=location)
            
            for zone in zones:
                sectors = zone.sectors.all()
                
                if sectors.count() == 1 and sectors.first().name == "":
                    # Handle zones with blank sectors
                    zone_marks = marks.filter(sector__zone=zone)
                    zone_average_mark = sum(mark.mark for mark in zone_marks) / len(zone_marks) if zone_marks else 0
                    zones_average_marks[zone.name] = {'blank_sector': zone_average_mark}
                else:
                    # Handle zones with non-blank sectors
                    has_non_blank_sectors = True  # Set the flag to True
                    sector_marks = {}
                    for sector in sectors:
                        sector_marks_queryset = marks.filter(sector=sector)
                        sector_average_mark = sum(mark.mark for mark in sector_marks_queryset) / len(sector_marks_queryset) if sector_marks_queryset else 0
                        sector_marks[sector.name] = sector_average_mark
                        
                    zones_average_marks[zone.name] = sector_marks

            # Update total_average_mark calculation
            if zones_average_marks:
                total_average_mark = sum(
                    [v['blank_sector'] if 'blank_sector' in v else sum(v.values())/len(v) for v in zones_average_marks.values()]
                ) / len(zones_average_marks)
    
            # Group marks and comments by time period (existing logic unchanged)
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
                        'zone': mark.sector.zone.name,
                        'sector': mark.sector.name,
                        'mark': mark.mark,
                        'customer_comment': customer_comment,
                        'contractor_comment': contractor_comment
                    }

                    if row not in same_time_period_rows:
                        same_time_period_rows.append(row)

                # Format the time period and date
                time_format = '%H:%M'
                date_format = '%Y-%m-%d'
                time_zone = pytz.timezone(earliest_mark.location.timezone)
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
        'has_non_blank_sectors': has_non_blank_sectors,  
    }

