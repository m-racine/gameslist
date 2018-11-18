# -*- coding: utf-8 -*-
from __future__ import unicode_literals



#import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
from django.db import models
from django.utils import timezone
from django.forms import ModelForm,DateField,SelectDateWidget
from django.core.exceptions import ValidationError
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

def no_future(value):
    today = date.today()
    if value > today:
        raise ValidationError('Purchase_Date/finish_date cannot be in the future.')

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
    notes = models.CharField(max_length=500,default="",blank=True, null=True)
    purchase_date = models.DateField('date purchased',default=date.today().isoformat(),validators=[no_future])
    finish_date = models.DateField('date finished', default=None, blank=True, null=True,validators=[no_future])
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    #substantial_progress = models.BooleanField(default=False)
    full_time_to_beat = models.FloatField(default=0.0)
    #time_to_beat = models.IntegerField(default=0)
    current_time = models.IntegerField(default=0)

    @property
    def aging(self):
        if self.beaten or self.abandoned:
            return self.finish_date - self.purchase_date
        return date.today() - self.purchase_date
    
    @property
    def play_aging(self):
        if self.played:
            return timedelta(0)
        return date.today() - self.purchase_date

    def save(self, *args, **kwargs):
        if self.full_time_to_beat == 0.0:
            self.full_time_to_beat = HowLongToBeat(self.name).fulltime
        super(Game, self).save(*args,**kwargs)

    def clean(self):
        if self.played and self.current_time <=0:
            raise ValidationError({'current_time':('If a game is played the current_time must be over 0.')})
        if self.finish_date and not (self.played and (self.beaten or self.abandoned)):
            raise ValidationError({'finish_date':('finish_date must be empty if game is not played and either beaten or abandoned.')})
        if self.finish_date:
            if self.finish_date < self.purchase_date:
                raise ValidationError({'finish_date':('finish_date must be after date of purchase.')})
        if self.beaten or self.abandoned:
            if not self.played:
                raise ValidationError({'played': ('You must have played a game to beat or abandon it.')})

    def __str__(self):
        return self.name + " - " + self.system

#class GameManager(models.Manager):
#    def create_game(self):
#        game = self.create()
    


class GameForm(ModelForm):
    class Meta:
        model = Game
        years = [x for x in range(datetime.now().year-9,datetime.now().year+1)]
        years.reverse()
        fields = ('name','system','location','game_format',
                  'played','beaten','abandoned','perler',
                  'reviewed','current_time','purchase_date','finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=years),
            'purchase_date': SelectDateWidget(years=years),
        }

class PlayBeatAbandonForm(ModelForm):
    class Meta:
        model = Game
        years = [x for x in range(datetime.now().year-9,datetime.now().year+1)]
        years.reverse()
        fields = ('played','current_time','beaten','abandoned','finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=years),
        }

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

