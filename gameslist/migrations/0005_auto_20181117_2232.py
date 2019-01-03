# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-18 03:32
from __future__ import unicode_literals

from django.db import migrations, models
import gameslist.models


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0004_auto_20181114_1526'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='current_time',
            field=models.IntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='game',
            name='finish_date',
            field=models.DateField(blank=True, default=None, null=True, validators=[gameslist.models.no_future], verbose_name='date finished'),
        ),
        migrations.AlterField(
            model_name='game',
            name='purchase_date',
            field=models.DateField(default=b'2018-11-17', validators=[gameslist.models.no_future], verbose_name='date purchased'),
        ),
    ]