# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-11-14 20:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0003_auto_20181114_0804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='finish_date',
            field=models.DateField(blank=True, default=None, null=True, verbose_name='date finished'),
        ),
        migrations.AlterField(
            model_name='game',
            name='full_time_to_beat',
            field=models.FloatField(default=0.0),
        ),
        migrations.AlterField(
            model_name='game',
            name='notes',
            field=models.CharField(blank=True, default='', max_length=500, null=True),
        ),
    ]
