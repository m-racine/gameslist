# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-09-28 16:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0004_gameinstance_steam_score'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='steamdata',
            name='current_time',
        ),
        migrations.RemoveField(
            model_name='steamdata',
            name='score',
        ),
    ]