# Generated by Django 5.1.1 on 2024-09-19 12:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_remove_comment_zone_remove_mark_zone_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='location',
            name='has_sectors',
            field=models.BooleanField(default=True, verbose_name='Имеет секторы'),
        ),
    ]
