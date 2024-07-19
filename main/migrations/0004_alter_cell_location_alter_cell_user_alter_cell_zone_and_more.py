# Generated by Django 5.0.7 on 2024-07-19 09:56

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_remove_cell_criterion_location_mark_range_max_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cell',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='cells', to='main.location'),
        ),
        migrations.AlterField(
            model_name='cell',
            name='user',
            field=models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='cells', to='main.user'),
        ),
        migrations.AlterField(
            model_name='cell',
            name='zone',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cells', to='main.zone'),
        ),
        migrations.AlterField(
            model_name='zone',
            name='created_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='zones', to='main.user'),
        ),
        migrations.AlterField(
            model_name='zone',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='zones', to='main.location'),
        ),
    ]
