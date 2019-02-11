# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-10 22:28
from __future__ import unicode_literals

from django.db import migrations, models
import gameslist.models


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0003_auto_20190117_1119'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='metacritic',
            field=models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero]),
        ),
        migrations.AddField(
            model_name='game',
            name='user_score',
            field=models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero]),
        ),
    ]
