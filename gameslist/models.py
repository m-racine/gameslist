# -*- coding: utf-8 -*-
from __future__ import unicode_literals



#import datetime
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
from django.db import models
#from django.utils import timezone
#from django.forms import DateField
#from django.forms import ModelForm, SelectDateWidget
from django.core.exceptions import ValidationError
#from endpoints.metacritic import MetaCritic
from endpoints.howlongtobeat import HowLongToBeat
from endpoints.metacritic import MetaCritic

LOGGER = logging.getLogger('MYAPP')

CURRENT_TIME_NOT_ALLOWED = 'Current time must be 0 if a game is unplayed.'
CURRENT_TIME_NEGATIVE = 'If a game is played the current_time must be over 0.'
FINISH_DATE_NOT_ALLOWED = "finish_date must be empty if game isn't played and beaten or abandoned."
NOT_PLAYED = 'You must have played a game to beat or abandon it.'
FINISH_AFTER_PURCHASE = 'finish_date must be after date of purchase.'
FINISH_DATE_REQUIRED = 'You must have a finish date to beat or abandon a game.'
# # Create your models here.

SYSTEMS = (
    ('3DS', 'Nintendo 3DS'),
    ('AND', 'Android'),
    ('ATA', 'Atari'),
    ('BNT', 'Battle.net'),
    ('DIG', 'Digipen'),
    ('NDS', 'Nintendo DS'),
    ('EPI', 'Epic Games'),
    ('GCN', 'Gamecube'),
    ('GB', 'Game Boy'),
    ('GBC', 'Game Boy Color'),
    ('GBA', 'Game Boy Advance'),
    ('GG', 'GameGear'),
    ('GOG', 'GoG'),
    ('HUM', 'Humble'),
    ('IND', 'IndieBox'),
    ('IIO', 'Itch.io'),
    ('KIN', 'Kindle'),
    ('NES', 'NES'),
    ('N64', 'Nintendo 64'),
    ('ORN', 'Origin'),
    ('PC', 'PC'),
    ('PSX', 'PlayStation'),
    ('PS2', 'PlayStation 2'),
    ('PS3', 'PlayStation 3'),
    ('PS4', 'PlayStation 4'),
    ('PSP', 'PlayStation Portable'),
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
    ('XB1', 'Xbox One')
)

def no_future(value):
    today = date.today()
    if value > today:
        raise ValidationError('Purchase_Date/finish_date cannot be in the future.')

def only_positive_or_zero(value):
    if value < 0:
        raise ValidationError('Value cannot be negative or zero.')
    return True


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
    game_format = models.CharField('format', max_length=1, choices=FORMATS, default='D')
    notes_old = models.CharField(max_length=500, default="", blank=True, null=True)
    #notes = models.ForeignKey(Note, on_delete=models.CASCADE, null=True)
    purchase_date = models.DateField('date purchased', default=None,
                                     validators=[no_future])
    finish_date = models.DateField('date finished', default=None, blank=True, null=True,
                                   validators=[no_future])
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)
    flagged = models.BooleanField(default=False)
    substantial_progress = models.BooleanField(default=False)
    full_time_to_beat = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    current_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    metacritic = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    user_score = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    priority = models.FloatField(default=0.0, validators=[only_positive_or_zero])

    @property
    def aging(self):
        if self.beaten or self.abandoned:
            if self.finish_date:
                return self.finish_date - self.purchase_date
            self.flagged = True
            LOGGER.warning("%s is lacking a finish_date", self.name)
            return date.today() - self.purchase_date
        return date.today() - self.purchase_date

    @property
    def play_aging(self):
        if self.played:
            return timedelta(0)
        return date.today() - self.purchase_date

    @property
    def time_to_beat(self):
        if self.beaten or self.abandoned:
            return 0.0
        return self.full_time_to_beat - self.current_time

    def save(self, *args, **kwargs):
        if self.full_time_to_beat == 0.0:
            self.full_time_to_beat = HowLongToBeat(self.name).fulltime
        if self.full_time_to_beat > 0:
            if self.current_time > (self.full_time_to_beat / 2):
                self.substantial_progress = True
        if self.metacritic == 0.0 or self.user_score == 0.0:
            meta = MetaCritic(self.name, self.get_system_display())
            self.metacritic = float(meta.metacritic)
            self.user_score = float(meta.userscore)
        self.priority = self.calculate_priority()
        super(Game, self).save(*args, **kwargs)

    def clean(self):
        super(Game, self).clean()
        if self.played and self.current_time <= 0:
            raise ValidationError({'current_time':(CURRENT_TIME_NEGATIVE)})
        if self.current_time > 0 and not self.played:
            raise ValidationError({'current_time':(CURRENT_TIME_NOT_ALLOWED)})
        if self.finish_date and not (self.beaten or self.abandoned):
            raise ValidationError({'finish_date':(FINISH_DATE_NOT_ALLOWED)})
        if self.finish_date:
            if self.finish_date < self.purchase_date:
                raise ValidationError({'finish_date':(FINISH_AFTER_PURCHASE)})
        if self.beaten or self.abandoned:
            if not self.played:
                raise ValidationError({'played': (NOT_PLAYED)})
            if self.finish_date is None:
                raise ValidationError({'finish_date': (FINISH_DATE_REQUIRED)})

    def calculate_priority(self):
        if self.beaten or self.abandoned:
            return 0.0
        score_factor = float(self.metacritic+(self.user_score*10))/float(self.full_time_to_beat)
        age_factor = float(self.aging / 365 * 12) * 0.25
        if self.played:
            return (age_factor +  score_factor)* 2
        return age_factor + score_factor

    def __str__(self):
        return self.name + " - " + self.system

    def __unicode__(self):
        return unicode(self.name) + u" - " + unicode(self.system)

#class GameManager(models.Manager):
#    def create_game(self):
#        game = self.create()



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


class Note(models.Model):
    text = models.CharField(max_length=500,default="",blank=True,null=True)
    date_added = models.DateField(null=False,validators=[no_future])
    date_last_modified = models.DateField(null=False,validators=[no_future])
    parent_game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.text

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
