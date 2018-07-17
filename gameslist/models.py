# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime

from django.db import models
from django.utils import timezone

# class Question(models.Model):
#     question_text = models.CharField(max_length=200)
#     pub_date = models.DateTimeField('date published')

#     def __str__(self):
#         return self.question_text

#     def was_published_recently(self):
#         now = timezone.now()
#         return (now - datetime.timedelta(days=1)) <= self.pub_date <= now

#     was_published_recently.admin_order_field = 'pub_date'
#     was_published_recently.boolean = True
#     was_published_recently.short_description = 'Published recently?'

# class Choice(models.Model):
#     question = models.ForeignKey(Question, on_delete=models.CASCADE)
#     choice_text = models.CharField(max_length=200)
#     votes = models.IntegerField(default=0)

#     def __str__(self):
#         return self.choice_text
# # Create your models here.

class Game(models.Model):
    SYSTEMS = (
        ('3DS', '3DS'),
        ('AND', 'Android'),
        ('DIG', 'Digipen'),
        ('NDS', 'DS'),
        ('GCN', 'Gamecube'),
        ('GBC', 'GBC'),
        ('GBA', 'GBA'),
        ('GOG', 'GoG'),
        ('HUM', 'Humble'),
        ('IIO', 'Itch.io'),
        ('KIN', 'Kindle'),
        ('NES', 'NES'),
        ('N64', 'N64'),
        ('ORN', 'Origin'),
        ('PC', 'PC'),
        ('PSX', 'Playstation'),
        ('PS2', 'Playstation 2'),
        ('PS3', 'Playstation 3'),
        ('PS4', 'Playstation 4'),
        ('SNS', 'SNES'),
        ('STM', 'Steam'),
        ('NSW', 'Switch'),
        ('TWH', 'Twitch'),
        ('UPL', 'Uplay'),
        ('VIT', 'Vita'),
        ('WII', 'Wii'),
        ('WIU', 'Wii U'),
        ('XBX', 'Xbox'),
        ('360', 'Xbox 360'),
        ('XB1', 'Xbox One'),
    )

    name = models.CharField(max_length=200)
    release_date = models.DateField('date released')
    system = models.CharField(max_length=3, choices=SYSTEMS)

class Owned(gameslist.Game):
    FORMATS = (
        ('P', 'Physical'),
        ('D', 'Digital'),
        ('M', 'Missing'),
        ('B', 'Borrowed'),
        ('N', 'None'),
    )

    location = models.CharField(max_length=3, choices=SYSTEMS)
    game_format = models.CharField('format',max_length=1, choices=FORMATS)
    series = models.CharField(max_length=100)
    developer = models.CharField(max_length=100)
    publisher = models.CharField(max_length=100)
    notes = models.CharField(max_length=500)
    purchase_date = models.DateField('date purchased')
    finish_date = models.DateField('date finished')
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    streamable = models.BooleanField(default=False)
    recordable = models.BooleanField(default=False)
    #adding new flag. indicates I super consciously sought it out
    pursued = models.BooleanField(default=False)
    #may have a different default
    substantial_progress = models.BooleanField(default=False)

    aging = models.IntegerField(default=0)
    play_aging = models.IntegerField(default=0)
    time_to_beat = models.IntegerField(default=0)
    current_time = models.IntegerField(default=0)
    number_of_eps = models.IntegerField(default=0)
    aging_effect = models.FloatField(default=0.0)
    aging_non_ep = models.IntegerField(default=0)
    priority = models.IntegerField(default=0)

    full_time_to_beat = models.IntegerField(default=0)
    number_of_players = models.IntegerField(default=0)
    times_recommended = models.IntegerField(default=0)
    times_passed_over = models.IntegerField(default=0)

    metacritic = models.FloatField(default=0.0)
    user_score = models.FloatField(default=0.0)

class Wish(gameslist.Game):
    #may have a different default
    #inherits name
    #inherit system as platform?
    date_added = models.DateField('date added')
    below_latte = models.BooleanField(default=False)

class PreferenceMap(models.Model):
    PREFERENCES = (
        (1, 'Greater Than'),
        (0, 'Neutral'),
        (-1, 'Less Than'),
    )
    source = models.ForeignKey(Game, on_delete=models.CASCADE)
    destination = models.ForeignKey(Game,  on_delete=models.CASCADE)
    preference = models.IntegerField(0)

    #its gonna be pretty sparese likely
    #so hmm
    #to be fair this is a bonus feature haha
    #so the above works for sparsity sure, but it's hell for like, every type of tracking status of ratnig everything



#HOW TO DEAL WITH PRICES OVER TIME??
#     stats
#     current price DECIMAL
#     current discount DECIMAL
#     lowest seen price DECIMAL
#     highest seen discount DECIMAL
#     base price? DECIMAL
#     length of time on wishlist


# #
# AutoField
# BigAutoField
# BigIntegerField
# BinaryField
# BooleanField
# CharField
# CommaSeparatedIntegerField
# DateField
# DateTimeField
# DecimalField
# DurationField
# EmailField
# FileField-kind of complicated
# FilePathField
# FloatField
# ImageField
# IntegerField
# GenericIPAddressField
# NullBooleanField
# PositiveIntegerField
# PositiveSmallIntegerField
# SlugField (short label)
# SmallIntegerField
# TextField
# TimeField
# URLField
# UUIDField

# ForeignKey
# ManyToManyField
# OneToOneField

#https://schier.co/blog/2014/12/05/html-templating-output-a-grid-in-a-single-loop.html

#Mikey, Rantasmo, Kyle Kallgren, Nella/Nellachronism, and I thiink Obscurus lupa