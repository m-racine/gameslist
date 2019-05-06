# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-03-02 20:24
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0009_auto_20190225_1118'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameToInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameslist.Game')),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameslist.GameInstance')),
                ('primary', models.BooleanField(default=True))
                ],
            options={
                'abstract': False,
            },
        ),
    ]
