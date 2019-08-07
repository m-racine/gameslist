# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-07-19 00:10
from __future__ import unicode_literals

from django.db import migrations
from django.db import models
from gameslist.models import only_positive_or_zero

class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0019_manual_20190801_1611'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='total_time',
            field=models.FloatField(default=0.0, validators=[only_positive_or_zero]),
        ),
    ]
