# Generated by Django 5.0.7 on 2024-07-15 16:55

import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='contractor_comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='contractor_comment_time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='cell',
            name='customer_comment',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='cell',
            name='customer_comment_time',
            field=models.TimeField(default=django.utils.timezone.now),
        ),
        migrations.AlterField(
            model_name='cell',
            name='mark',
            field=models.SmallIntegerField(choices=[(0, 0), (1, 1), (2, 2), (3, 3), (4, 4), (5, 5)]),
        ),
        migrations.AlterField(
            model_name='cell',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, to='main.user'),
        ),
    ]
