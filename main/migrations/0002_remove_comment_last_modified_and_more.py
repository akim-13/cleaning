# Generated by Django 5.0.7 on 2024-08-14 14:45

import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='comment',
            name='last_modified',
        ),
        migrations.RemoveField(
            model_name='mark',
            name='last_modified',
        ),
        migrations.AddField(
            model_name='comment',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
        migrations.AddField(
            model_name='mark',
            name='timestamp',
            field=models.DateTimeField(default=django.utils.timezone.now),
        ),
    ]