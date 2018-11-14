# -*- coding: utf-8 -*-
from __future__ import unicode_literals



#import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
from django.db import models
from django.utils import timezone
from django.forms import ModelForm
from endpoints.metacritic import MetaCritic
from endpoints.howlongtobeat import HowLongToBeat

logger = logging.getLogger('MYAPP')

# # Create your models here.

SYSTEMS = (
    ('3DS', 'Nintendo 3DS'),
    ('AND', 'Android'),
    ('ATA', 'Atari'),
    ('BNT', 'Battle.net'),
    ('DIG', 'Digipen'),
    ('NDS', 'Nintendo DS'),
    ('GCN', 'Gamecube'),
    ('GB',  'Game Boy'),
    ('GBC', 'Game Boy Color'),
    ('GBA', 'Game Boy Advance'),
    ('GG',  'GameGear'),
    ('GOG', 'GoG'),
    ('HUM', 'Humble'),
    ('IND', 'IndieBox'),
    ('IIO', 'Itch.io'),
    ('KIN', 'Kindle'),
    ('NES', 'Nintendo Entertainment System'),
    ('N64', 'Nintendo 64'),
    ('ORN', 'Origin'),
    ('PC', 'PC'),
    ('PSX', 'PlayStation'),
    ('PS2', 'PlayStation 2'),
    ('PS3', 'PlayStation 3'),
    ('PS4', 'PlayStation 4'),
    ('PSP', 'PlayStation Portable'),
    ('SNS', 'Super Nintendo Entertainment System'),
    ('STM', 'Steam'),
    ('NSW', 'Switch'),
    ('TWH', 'Twitch'),
    ('UPL', 'Uplay'),
    ('VIT', 'Vita'),
    ('WII', 'Wii'),
    ('WIU', 'Wii U'),
    ('XBX', 'Xbox'),
    ('360', 'Xbox 360'),
    ('XB1', 'Xbox One')
)

class Game(models.Model):
    FORMATS = (
        ('P', 'Physical'),
        ('D', 'Digital'),
        ('M', 'Missing'),
        ('B', 'Borrowed'),
        ('N', 'None'),
        ('R', 'Returned'),
        ('L', 'Lent'),
        ('E', 'Expired')
    )
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, default="")
    system = models.CharField(max_length=3, choices=SYSTEMS, default="STM")
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    location = models.CharField(max_length=3, choices=SYSTEMS, default='STM')
    game_format = models.CharField('format',max_length=1, choices=FORMATS, default='D')
    notes = models.CharField(max_length=500,default="",blank=True)
    purchase_date = models.DateField('date purchased',default=date.today().isoformat())
    finish_date = models.DateField('date finished', default=None, blank=True)
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)

    @property
    def aging(self):
        if self.beaten or self.abandoned:
            #logger.debug(type(self.finish_date-self.purchase_date.days()))
            #return datetime.strptime(self.finish_date,"%Y-%m-%d")-datetime.strptime(self.purchase_date,"%Y-%m-%d")
            return self.finish_date - self.purchase_date
        #return date.today() - datetime.strptime(self.purchase_date,"%Y-%m-%d")
        return date.today() - self.purchase_date
    
    @property
    def play_aging(self):
        if self.played:
            return timedelta(0)
        return date.today() - self.purchase_date
    
    #aging = models.IntegerField(default=0)
    #play_aging = models.IntegerField(default=0)

    def __str__(self):
        return self.name + " - " + self.system

class GameManager(models.Manager):
    def create_game(self):
        game = self.create()


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ['name','system','location','game_format',
                  'played','beaten','abandoned','perler',
                  'reviewed','purchase_date','finish_date']

class Wish(models.Model):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, default="")
    system = models.CharField(max_length=3, choices=SYSTEMS, default='STM')
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    date_added = models.DateField('date added', default=date.today)
    below_latte = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " - " + self.system

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

