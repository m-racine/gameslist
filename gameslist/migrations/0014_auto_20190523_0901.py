# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-05-23 14:01
from __future__ import unicode_literals

from django.db import migrations, models
import gameslist.models


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0013_auto_20190310_1722'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='gameinstance',
            name='full_time_to_beat',
        ),
        migrations.RemoveField(
            model_name='gameinstance',
            name='priority',
        ),
        migrations.RemoveField(
            model_name='gameinstance',
            name='times_passed_over',
        ),
        migrations.RemoveField(
            model_name='gameinstance',
            name='times_recommended',
        ),
        migrations.AddField(
            model_name='game',
            name='full_time_to_beat',
            field=models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero]),
        ),
        migrations.AddField(
            model_name='game',
            name='total_time',
            field=models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero]),
        ),
    ]
