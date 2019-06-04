# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#import datetime
import sys
from datetime import date
from datetime import datetime
from datetime import timedelta
import logging
import traceback
from django.db import models
#from django.utils import timezone
#from django.forms import DateField
#from django.forms import ModelForm, SelectDateWidget
from django.core.exceptions import ValidationError
#from endpoints.metacritic import MetaCritic
from endpoints.howlongtobeat import HowLongToBeat
from endpoints.metacritic import MetaCritic
from misc.names import gen_names, gen_metacritic_names

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

#ENTITIES
GAME = 1
GAME_INSTANCE = 2
NOTE = 3
ALTERNATE_NAME = 4
WISH = 5
SERIES = 6
SUB_SERIES = 7

def no_future(value):
    today = date.today()
    if value > today:
        raise ValidationError('Purchase_Date/finish_date cannot be in the future.')

def only_positive_or_zero(value):
    if value < 0:
        raise ValidationError('Value cannot be negative or zero.')
    return True

class BaseModel(models.Model):
    created_date = models.DateField(default=None,editable=False)
    modified_date = models.DateField(default=None,editable=False)
    flagged = models.BooleanField(default=False)
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.modified_date = datetime.now()
        if not self.created_date:
            self.created_date = datetime.now()
        super(BaseModel, self).save(*args, **kwargs)

#developer
#publisher
#pursued
#number_of_players
#streamable
#recordable

class Game(BaseModel):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, default="")
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    #notes = models.ForeignKey(Note, on_delete=models.CASCADE, null=True)
    purchase_date = models.DateField('date purchased', default=None,
                                     validators=[no_future])
    finish_date = models.DateField('date finished', default=None, blank=True, null=True,
                                   validators=[no_future])
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    #not a property so that it can be sorted more easily.
    priority = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    times_recommended = models.IntegerField(default=0,validators=[only_positive_or_zero])
    times_passed_over = models.IntegerField(default=0,validators=[only_positive_or_zero])
    full_time_to_beat = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    total_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])


    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.strip(" ")
        if self.full_time_to_beat <= 0.0:
            self.full_time_to_beat = self.calculate_how_long_to_beat()

        super(Game, self).save(*args, **kwargs)

    def calculate_how_long_to_beat(self):
        names_list = [self.name] + list(AlternateName.objects.all().filter(parent_entity=self.id))
        for name in names_list:
            try:
                if type(name) == AlternateName:
                    fulltime = HowLongToBeat(name.text).fulltime
                else:
                    fulltime = HowLongToBeat(self.name).fulltime
                if fulltime > 0.0:
                    return fulltime
                elif fulltime == -1.0:
                    LOGGER.warning("Found %s, no time recorded", name)
                    return fulltime
            except:
                LOGGER.error("HLTB FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        names_to_try = gen_names(self.name)
        #LOGGER.warning(names_to_try)
        if len(names_to_try) > 1000:
            return -2.0
        for name in names_to_try:
            try:
                fulltime = HowLongToBeat(name).fulltime
                if fulltime > 0.0:
                    alt = AlternateName.create(text=name,parent_entity=self)
                    alt.save()
                    return fulltime
                elif fulltime == -1.0:
                    LOGGER.warning("Found %s, no time recorded", name)
                    alt = AlternateName.create(text=name,parent_entity=self)
                    alt.save()
                    return fulltime
            except:
                LOGGER.error("HLTB FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        return -1.0

class GameInstance(BaseModel):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, default="")
    system = models.CharField(max_length=3, choices=SYSTEMS, default="STM")
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    location = models.CharField(max_length=3, choices=SYSTEMS, default='STM')
    game_format = models.CharField('format', max_length=1, choices=FORMATS, default='D')
    #notes = models.ForeignKey(Note, on_delete=models.CASCADE, null=True)
    purchase_date = models.DateField('date purchased', default=None,
                                     validators=[no_future])
    finish_date = models.DateField('date finished', default=None, blank=True, null=True,
                                   validators=[no_future])
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    substantial_progress = models.BooleanField(default=False)
    current_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    metacritic = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    user_score = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    #not a property so that it can be sorted more easily.


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

    # @property
    # def time_to_beat(self):
    #     if self.beaten or self.abandoned:
    #         return 0.0
    #     return self.full_time_to_beat - self.current_time

    def save(self, *args, **kwargs):
        self.name = self.name.strip(" ")
        # if self.full_time_to_beat <= 0.0:
        #     self.full_time_to_beat = self.calculate_how_long_to_beat()
        # if self.full_time_to_beat > 0:
        #     if self.current_time > (self.full_time_to_beat / 2):
        #         self.substantial_progress = True
        #     else:
        #         self.substantial_progress = False
        # else:
        #     self.substantial_progress = False
        if self.metacritic <= 0.0 or self.user_score <= 0.0:
            (self.metacritic,self.user_score) = self.calculate_metacritic()
        #temp
        #if self.priority < 1.0:
        # self.priority = self.calculate_priority()
        # if self.priority == 0.0:
        #     self.priority = -5.0
        super(GameInstance, self).save(*args, **kwargs)

    def clean(self):
        super(GameInstance, self).clean()
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

    def calculate_metacritic(self):
        names_list = [self.name] + list(AlternateName.objects.all().filter(parent_entity=self.id))
        for name in names_list:
            try:
                if type(name) == AlternateName:
                    meta = MetaCritic(name.text, self.get_system_display())
                else:
                    meta = MetaCritic(name, self.get_system_display())
                metacritic = float(meta.metacritic)
                user_score = float(meta.userscore)
                if metacritic > 0 or user_score > 0:
                    return (metacritic, user_score)
                if metacritic == -2.0 or user_score == -2.0:
                    LOGGER.warning("Found %s, not full scores", name)
                    return (metacritic, user_score)
            except:
                LOGGER.error("METACRITIC FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        #LOGGER.debug(self.name)
        names_to_try = gen_metacritic_names(self.name)
        #LOGGER.warning(names_to_try)
        if len(names_to_try) > 1000:
            return (-2.0, -2.0)
        for name in names_to_try:
            try:
                meta = MetaCritic(name, self.get_system_display())
                metacritic = float(meta.metacritic)
                user_score = float(meta.userscore)
                if metacritic > 0.0 or user_score > 0.0:
                    alt = AlternateName.create(text=name,parent_game=self)
                    alt.save()
                    return (metacritic, user_score)
                if metacritic == -2.0 or user_score == -2.0:
                    LOGGER.warning("Found %s, not full scores", name)
                    alt = AlternateName.create(text=name,parent_game=self)
                    alt.save()
                    return (metacritic, user_score)
            except:
                LOGGER.error("MetaCritic FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        return (-1.0,-1.0)

    def calculate_how_long_to_beat(self):
        names_list = [self.name] + list(AlternateName.objects.all().filter(parent_game=self.id))
        for name in names_list:
            try:
                if type(name) == AlternateName:
                    fulltime = HowLongToBeat(name.text).fulltime
                else:
                    fulltime = HowLongToBeat(self.name).fulltime
                if fulltime > 0.0:
                    return fulltime
                elif fulltime == -1.0:
                    LOGGER.warning("Found %s, no time recorded", name)
                    return fulltime
            except:
                LOGGER.error("HLTB FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        names_to_try = gen_names(self.name)
        #LOGGER.warning(names_to_try)
        if len(names_to_try) > 1000:
            return -2.0
        for name in names_to_try:
            try:
                fulltime = HowLongToBeat(name).fulltime
                if fulltime > 0.0:
                    alt = AlternateName.create(text=name,parent_game=self)
                    alt.save()
                    return fulltime
                elif fulltime == -1.0:
                    LOGGER.warning("Found %s, no time recorded", name)
                    alt = AlternateName.create(text=name,parent_game=self)
                    alt.save()
                    return fulltime
            except:
                LOGGER.error("HLTB FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        return -1.0

    def calculate_priority(self):
        try:
            if self.beaten or self.abandoned:
                return -1.0
            if self.game_format in ["M","R","E","L","N"]:
                return -2.0
            score_factor = float(self.metacritic+(self.user_score*10.0))/float(self.full_time_to_beat)
            if score_factor < 0.0:
                score_factor = 0.0
            age_factor = ((self.aging.days / 365.0) * 12.0) * 0.5
            rec_factor = float(1 + self.times_recommended) / float(1 + self.times_passed_over)
            LOGGER.debug("score: %2.f age: %2.f rec %2.f",score_factor,age_factor,rec_factor)
            misc_factor = 1.0
            if self.played:
                misc_factor += 1.0
            if self.game_format == "B":
                misc_factor += 1.0
            if self.substantial_progress:
                misc_factor += 1.0
            prior = round(((age_factor +  score_factor)* misc_factor) * rec_factor,2)
            if round(prior,1) == 0.0:
                return -3.0
            return prior
        except:
            pass
        return -4.0

    def __str__(self):
        return self.name + " - " + self.system

    def __unicode__(self):
        return unicode(self.name) + u" - " + unicode(self.system)

#class GameManager(models.Manager):
#    def create_game(self):
#        game = self.create()


class GameToInstance(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
    primary = models.BooleanField(default=True)

class Wish(BaseModel):
    #id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200, default="")
    system = models.CharField(max_length=3, choices=SYSTEMS, default='STM')
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    date_added = models.DateField('date added', default=date.today)
    below_latte = models.BooleanField(default=False)

    def __str__(self):
        return self.name + " - " + self.system


class Note(BaseModel):
    note = models.CharField(max_length=500,default="",blank=True,null=True)
    parent_entity = models.IntegerField(default=1,null=False)
    parent_entity_type = models.IntegerField(default=1)
    def __str__(self):
        return self.note

class Flag(BaseModel):
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(default=None)
    note = models.CharField(max_length=500,default="",blank=True,null=True)
    parent_entity = models.IntegerField(default=1,null=False)
    parent_entity_type = models.IntegerField(default=1)
    def __str__(self):
        return self.note

class AlternateName(BaseModel):
    parent_entity = models.IntegerField(default=1,null=False)
    name = models.CharField(max_length=200,default="",blank=True,null=True)
    parent_entity_type = models.IntegerField(default=1)

    def __str__(self):
        return self.text

    @classmethod
    def create(cls, name, parent_game):
        name = cls(name=name, parent_game=parent_game, created_date=date.today(),modified_date=date.today())
        # do something with the book
        return name

class Series(BaseModel):
    name = models.CharField(max_length=200,default="",blank=True,null=True)
    linear = models.BooleanField(default=False)

class SubSeries(BaseModel):
    name = models.CharField(max_length=200,default="",blank=True,null=True)
    linear = models.BooleanField(default=False)
    parent_series = models.ForeignKey(Series,  on_delete=models.CASCADE, null=True)

class GameToSeries(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
    series = models.ForeignKey(Series, on_delete=models.CASCADE, null=True)
    subseries = models.ForeignKey(SubSeries, on_delete=models.CASCADE, null=True)

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
