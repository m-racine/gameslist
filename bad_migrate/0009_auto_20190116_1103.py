# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2019-01-16 16:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import gameslist.models


class Migration(migrations.Migration):

    dependencies = [
        ('gameslist', '0008_auto_20181128_1556'),
    ]

    operations = [
        migrations.CreateModel(
            name='Note',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text', models.CharField(blank=True, default='', max_length=500, null=True)),
                ('date_added', models.DateField(validators=[gameslist.models.no_future])),
                ('date_last_modified', models.DateField(validators=[gameslist.models.no_future])),
            ],
        ),
        migrations.AlterField(
            model_name='game',
            name='location',
            field=models.CharField(choices=[('3DS', 'Nintendo 3DS'), ('AND', 'Android'), ('ATA', 'Atari'), ('BNT', 'Battle.net'), ('DIG', 'Digipen'), ('NDS', 'Nintendo DS'), ('EPI', 'Epic Games'), ('GCN', 'Gamecube'), ('GB', 'Game Boy'), ('GBC', 'Game Boy Color'), ('GBA', 'Game Boy Advance'), ('GG', 'GameGear'), ('GOG', 'GoG'), ('HUM', 'Humble'), ('IND', 'IndieBox'), ('IIO', 'Itch.io'), ('KIN', 'Kindle'), ('NES', 'NES'), ('N64', 'Nintendo 64'), ('ORN', 'Origin'), ('PC', 'PC'), ('PSX', 'PlayStation'), ('PS2', 'PlayStation 2'), ('PS3', 'PlayStation 3'), ('PS4', 'PlayStation 4'), ('PSP', 'PlayStation Portable'), ('SNS', 'SNES'), ('STM', 'Steam'), ('NSW', 'Switch'), ('TWH', 'Twitch'), ('UPL', 'Uplay'), ('VIT', 'Vita'), ('WII', 'Wii'), ('WIU', 'Wii U'), ('XBX', 'Xbox'), ('360', 'Xbox 360'), ('XB1', 'Xbox One')], default='STM', max_length=3),
        ),
        # migrations.AlterField(
        #     model_name='game',
        #     name='notes',
        #     field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='gameslist.Note'),
        # ),
        migrations.AlterField(
            model_name='game',
            name='system',
            field=models.CharField(choices=[('3DS', 'Nintendo 3DS'), ('AND', 'Android'), ('ATA', 'Atari'), ('BNT', 'Battle.net'), ('DIG', 'Digipen'), ('NDS', 'Nintendo DS'), ('EPI', 'Epic Games'), ('GCN', 'Gamecube'), ('GB', 'Game Boy'), ('GBC', 'Game Boy Color'), ('GBA', 'Game Boy Advance'), ('GG', 'GameGear'), ('GOG', 'GoG'), ('HUM', 'Humble'), ('IND', 'IndieBox'), ('IIO', 'Itch.io'), ('KIN', 'Kindle'), ('NES', 'NES'), ('N64', 'Nintendo 64'), ('ORN', 'Origin'), ('PC', 'PC'), ('PSX', 'PlayStation'), ('PS2', 'PlayStation 2'), ('PS3', 'PlayStation 3'), ('PS4', 'PlayStation 4'), ('PSP', 'PlayStation Portable'), ('SNS', 'SNES'), ('STM', 'Steam'), ('NSW', 'Switch'), ('TWH', 'Twitch'), ('UPL', 'Uplay'), ('VIT', 'Vita'), ('WII', 'Wii'), ('WIU', 'Wii U'), ('XBX', 'Xbox'), ('360', 'Xbox 360'), ('XB1', 'Xbox One')], default='STM', max_length=3),
        ),
        migrations.AlterField(
            model_name='wish',
            name='system',
            field=models.CharField(choices=[('3DS', 'Nintendo 3DS'), ('AND', 'Android'), ('ATA', 'Atari'), ('BNT', 'Battle.net'), ('DIG', 'Digipen'), ('NDS', 'Nintendo DS'), ('EPI', 'Epic Games'), ('GCN', 'Gamecube'), ('GB', 'Game Boy'), ('GBC', 'Game Boy Color'), ('GBA', 'Game Boy Advance'), ('GG', 'GameGear'), ('GOG', 'GoG'), ('HUM', 'Humble'), ('IND', 'IndieBox'), ('IIO', 'Itch.io'), ('KIN', 'Kindle'), ('NES', 'NES'), ('N64', 'Nintendo 64'), ('ORN', 'Origin'), ('PC', 'PC'), ('PSX', 'PlayStation'), ('PS2', 'PlayStation 2'), ('PS3', 'PlayStation 3'), ('PS4', 'PlayStation 4'), ('PSP', 'PlayStation Portable'), ('SNS', 'SNES'), ('STM', 'Steam'), ('NSW', 'Switch'), ('TWH', 'Twitch'), ('UPL', 'Uplay'), ('VIT', 'Vita'), ('WII', 'Wii'), ('WIU', 'Wii U'), ('XBX', 'Xbox'), ('360', 'Xbox 360'), ('XB1', 'Xbox One')], default='STM', max_length=3),
        ),
    ]
