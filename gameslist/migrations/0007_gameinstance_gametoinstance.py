# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-02-22 22:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import gameslist.models


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0006_auto_20190212_1629'),
    ]

    operations = [
        migrations.CreateModel(
            name='GameInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_date', models.DateField(default=None, editable=False)),
                ('modified_date', models.DateField(default=None, editable=False)),
                ('name', models.CharField(default='', max_length=200)),
                ('system', models.CharField(choices=[('3DS', 'Nintendo 3DS'), ('AND', 'Android'), ('ATA', 'Atari'), ('BNT', 'Battle.net'), ('DIG', 'Digipen'), ('NDS', 'Nintendo DS'), ('EPI', 'Epic Games'), ('GCN', 'Gamecube'), ('GB', 'Game Boy'), ('GBC', 'Game Boy Color'), ('GBA', 'Game Boy Advance'), ('GG', 'GameGear'), ('GOG', 'GoG'), ('HUM', 'Humble'), ('IND', 'IndieBox'), ('IIO', 'Itch.io'), ('KIN', 'Kindle'), ('NES', 'NES'), ('N64', 'Nintendo 64'), ('ORN', 'Origin'), ('PC', 'PC'), ('PSX', 'PlayStation'), ('PS2', 'PlayStation 2'), ('PS3', 'PlayStation 3'), ('PS4', 'PlayStation 4'), ('PSP', 'PlayStation Portable'), ('SNS', 'SNES'), ('STM', 'Steam'), ('NSW', 'Switch'), ('TWH', 'Twitch'), ('UPL', 'Uplay'), ('VIT', 'Vita'), ('WII', 'Wii'), ('WIU', 'Wii U'), ('XBX', 'Xbox'), ('360', 'Xbox 360'), ('XB1', 'Xbox One')], default='STM', max_length=3)),
                ('played', models.BooleanField(default=False)),
                ('beaten', models.BooleanField(default=False)),
                ('location', models.CharField(choices=[('3DS', 'Nintendo 3DS'), ('AND', 'Android'), ('ATA', 'Atari'), ('BNT', 'Battle.net'), ('DIG', 'Digipen'), ('NDS', 'Nintendo DS'), ('EPI', 'Epic Games'), ('GCN', 'Gamecube'), ('GB', 'Game Boy'), ('GBC', 'Game Boy Color'), ('GBA', 'Game Boy Advance'), ('GG', 'GameGear'), ('GOG', 'GoG'), ('HUM', 'Humble'), ('IND', 'IndieBox'), ('IIO', 'Itch.io'), ('KIN', 'Kindle'), ('NES', 'NES'), ('N64', 'Nintendo 64'), ('ORN', 'Origin'), ('PC', 'PC'), ('PSX', 'PlayStation'), ('PS2', 'PlayStation 2'), ('PS3', 'PlayStation 3'), ('PS4', 'PlayStation 4'), ('PSP', 'PlayStation Portable'), ('SNS', 'SNES'), ('STM', 'Steam'), ('NSW', 'Switch'), ('TWH', 'Twitch'), ('UPL', 'Uplay'), ('VIT', 'Vita'), ('WII', 'Wii'), ('WIU', 'Wii U'), ('XBX', 'Xbox'), ('360', 'Xbox 360'), ('XB1', 'Xbox One')], default='STM', max_length=3)),
                ('game_format', models.CharField(choices=[('P', 'Physical'), ('D', 'Digital'), ('M', 'Missing'), ('B', 'Borrowed'), ('N', 'None'), ('R', 'Returned'), ('L', 'Lent'), ('E', 'Expired')], default='D', max_length=1, verbose_name='format')),
                ('notes_old', models.CharField(blank=True, default='', max_length=500, null=True)),
                ('purchase_date', models.DateField(default=None, validators=[gameslist.models.no_future], verbose_name='date purchased')),
                ('finish_date', models.DateField(blank=True, default=None, null=True, validators=[gameslist.models.no_future], verbose_name='date finished')),
                ('abandoned', models.BooleanField(default=False)),
                ('perler', models.BooleanField(default=False)),
                ('reviewed', models.BooleanField(default=False)),
                ('flagged', models.BooleanField(default=False)),
                ('substantial_progress', models.BooleanField(default=False)),
                ('full_time_to_beat', models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero])),
                ('current_time', models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero])),
                ('metacritic', models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero])),
                ('user_score', models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero])),
                ('priority', models.FloatField(default=0.0, validators=[gameslist.models.only_positive_or_zero])),
                ('times_recommended', models.IntegerField(default=0, validators=[gameslist.models.only_positive_or_zero])),
                ('times_passed_over', models.IntegerField(default=0, validators=[gameslist.models.only_positive_or_zero])),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='GameToInstance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('game', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameslist.Game')),
                ('instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='gameslist.GameInstance')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]