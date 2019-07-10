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
from django.core.exceptions import ValidationError
from howlongtobeat import HowLongToBeat
from metacritic import MetaCritic
from names import gen_names, gen_metacritic_names
from django.shortcuts import render,get_object_or_404

LOGGER = logging.getLogger('MYAPP') # pragma: no cover

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

STATUSES = (
    ('O', 'Owned'),
    ('B', 'Borrowed'),
    ('N', 'None')
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
FLAG = 8

def no_future(value):
    today = date.today()
    if value > today:
        raise ValidationError('Purchase_Date/finish_date cannot be in the future.')
    return True

def only_positive_or_zero(value):
    if (type(value) == int or type(value) == float):
        if value < 0:
            raise ValidationError('Value cannot be negative or zero.')
    else:
        raise ValidationError('Value must be a number.')
    return True

def map_single_game_instance(game_id):
    print "MAPPING"
    game = get_object_or_404(GameInstance, pk=game_id)
    mapping = GameToInstance.objects.all().filter(instance_id=game.id)
    LOGGER.debug(mapping)
    if mapping.count() > 0:
        LOGGER.debug("Mapping found for %s", game)
        return
    else:
        try:
            name_list = [game.name] + list(AlternateName.objects.all().filter(parent_entity=game.id))
            LOGGER.error(name_list)
            for name in name_list:
                LOGGER.debug(name)
                masters = Game.objects.filter(name=name)
                if masters.count() > 1:
                    LOGGER.debug("Too many matches for %s for %s", name, game)
                    break
                elif masters.count() == 1:
                    LOGGER.info("Creating mapping from %s to %s", game, masters[0])
                    g_to_i = GameToInstance.objects.create(game=masters[0], instance=game, primary=False)
                    #g_to_i.save()
                    break
                else:
                    LOGGER.debug("Creating new master game for %s", game)
                    master_game = Game.objects.create_game(name=game.name, played=game.played, beaten=game.beaten,
                                                     purchase_date=game.purchase_date, finish_date=game.finish_date,
                                                     abandoned=game.abandoned,
                                                     flagged=game.flagged)
                    #master_game.save()

                    LOGGER.debug("Mapping new master game %s to %s", master_game, game)
                    g_to_i = GameToInstance.objects.create(game=master_game, instance=game, primary=True)
                    #g_to_i.save()
                    LOGGER.info("Added %s", master_game.name)

                    break
        except:
            LOGGER.error(sys.exc_info()[0])
            LOGGER.error(sys.exc_info()[1])
            LOGGER.error(traceback.print_tb(sys.exc_info()[2]))

def convert_date_fields(model_dict):
    if 'purchase_date_year' in model_dict:
        try:
            model_dict['purchase_date'] = date(int(model_dict['purchase_date_year']),int(model_dict['purchase_date_month']),int(model_dict['purchase_date_day']))
        except ValueError:
            model_dict['purchase_date'] = date.today()
            LOGGER.warning("Invalid date: %d-%d-%d",int(model_dict['purchase_date_year']),int(model_dict['purchase_date_month']),int(model_dict['purchase_date_day']))
        finally:
            del model_dict['purchase_date_year']
            del model_dict['purchase_date_month']
            del model_dict['purchase_date_day']
    if 'finish_date_year' in model_dict:
        try:
            model_dict['finish_date'] = date(int(model_dict['finish_date_year']),int(model_dict['finish_date_month']),int(model_dict['finish_date_day']))
        except ValueError:
            model_dict['finish_date'] = date.today()
            LOGGER.warning("Invalid date: %d-%d-%d",int(model_dict['finish_date_year']),int(model_dict['finish_date_month']),int(model_dict['finish_date_day']))
        finally:
            del model_dict['finish_date_year']
            del model_dict['finish_date_month']
            del model_dict['finish_date_day']
    return model_dict

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
class GameManager(models.Manager):
    def create_game(self,name="Portal", played=False, beaten=False,
                    purchase_date=None, finish_date=None, substantial_progress=False,
                    abandoned=False, perler=False, flagged=False,
                    priority=0, times_recommended=0, times_passed_over=0,
                    full_time_to_beat=0.0, total_time=0.0, status='O'):
        game = self.create(name=name, played=played, beaten=beaten,
                                   purchase_date=purchase_date, finish_date=finish_date,
                                   abandoned=abandoned, perler=perler,
                                   substantial_progress=substantial_progress,
                                   flagged=flagged, priority=priority, times_recommended=times_recommended,
                                   times_passed_over=times_passed_over, full_time_to_beat=full_time_to_beat,
                                   total_time=total_time)
        #(game.metacritic,game.user_score) = game.calculate_metacritic()
        game.priority = game.calculate_priority()
        game.save()
        return game

class Game(BaseModel):
    #id = models.AutoField(primary_key=True)
    objects = GameManager()
    status = models.CharField(max_length=3, choices=STATUSES, default="O")
    name = models.CharField(max_length=200, default="")
    played = models.BooleanField(default=False) #calculated from child instances
    beaten = models.BooleanField(default=False) #calculated from child instances
    #notes = models.ForeignKey(Note, on_delete=models.CASCADE, null=True)
    purchase_date = models.DateField('date purchased', default=None,
                                     validators=[no_future]) #calculated from child instances
    finish_date = models.DateField('date finished', default=None, blank=True, null=True,
                                   validators=[no_future]) #calculated from child instances
    abandoned = models.BooleanField(default=False) #calculated from child instances
    perler = models.BooleanField(default=False)
    #not a property so that it can be sorted more easily.
    priority = models.FloatField(default=0.0, validators=[only_positive_or_zero]) #calculated from child instances
    substantial_progress = models.BooleanField(default=False) #calculated from child instances
    times_recommended = models.IntegerField(default=0,validators=[only_positive_or_zero])
    times_passed_over = models.IntegerField(default=0,validators=[only_positive_or_zero])
    full_time_to_beat = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    total_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    aging = models.IntegerField(default=0,validators=[only_positive_or_zero])
    play_aging = models.IntegerField(default=0,validators=[only_positive_or_zero])
    average_score = models.FloatField(default=0.0)


    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        self.name = self.name.strip(" ")
        if self.full_time_to_beat <= 0.0:
            self.full_time_to_beat = self.calculate_how_long_to_beat()
        if self.beaten or self.abandoned:
                 if self.finish_date:
                     self.aging = (self.finish_date - self.purchase_date).days
                 else:
                     self.flagged = True
                     LOGGER.warning("%s is lacking a finish_date", self.name)
                     self.aging = (date.today() - self.purchase_date).days
        else:
             self.aging = (date.today() - self.purchase_date).days
        if self.played:
            self.play_aging = 0
        else:
            self.play_aging = (date.today() - self.purchase_date).days
        super(Game, self).save(*args, **kwargs)

    def update_from_children(self):
        instance_mappings = GameToInstance.objects.filter(game_id=self.id)
        instance_ids = []
        if instance_mappings.count() == 0:
            return
        for inm in instance_mappings:
            instance_ids.append(inm.instance_id)
        instances = GameInstance.objects.filter(pk__in=instance_ids)
        score_sum = 0.0
        time_sum = 0.0
        instance_missing = False
        instance_borrowed = False
        instance_owned = False
        for instance in instances:
            if instance.beaten:
                self.beaten = True
            if instance.played:
                self.played = True
            if instance.finish_date:
                if self.finish_date:
                    if instance.finish_date < self.finish_date:
                        self.finish_date = instance.finish_date
                else:
                    self.finish_date = instance.finish_date
            score_sum += instance.metacritic + (instance.user_score*10.0)
            if instance.current_time > (self.full_time_to_beat /2.0):
                self.substantial_progress = True
            time_sum += instance.current_time
            if instance.game_format == "B":
                instance_borrowed = True
            elif instance.game_format in ["M","R","E","L","N"]:
                instance_missing = True
            else:
                instance_owned = True
        if instance_borrowed:
            self.status = "B"
        elif instance_owned:
            self.status = "O"
        elif instance_missing:
            self.status = "N"
        self.average_score = score_sum/instances.count()
        self.total_time = time_sum

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

    def calculate_priority(self):
        self.update_from_children()
        try:
            if self.beaten or self.abandoned:
                return -1.0
            if self.status == "N":
                return -2.0
            score_factor = self.average_score/float(self.full_time_to_beat)
            if score_factor < 0.0:
                score_factor = 0.0
            age_factor = ((self.aging.days / 365.0) * 12.0) * 0.5
            rec_factor = float(1 + self.times_recommended) / float(1 + self.times_passed_over)
            LOGGER.debug("score: %2.f age: %2.f rec %2.f",score_factor,age_factor,rec_factor)
            misc_factor = 1.0
            if self.played:
                misc_factor += 1.0
            if self.status == "B":
                misc_factor += 1.0
            #if self.substantial_progress:
            #   misc_factor += 1.0
            prior = round(((age_factor +  score_factor)* misc_factor) * rec_factor,2)
            if round(prior,1) == 0.0:
                return -3.0
            return prior
        except:
            pass
        return -4.0
    # @property
    # def aging(self):
    #     if self.beaten or self.abandoned:
    #         if self.finish_date:
    #             return self.finish_date - self.purchase_date
    #         self.flagged = True
    #         LOGGER.warning("%s is lacking a finish_date", self.name)
    #         return date.today() - self.purchase_date
    #     return date.today() - self.purchase_date
    #
    # @property
    # def play_aging(self):
    #     if self.played:
    #         return timedelta(0)
    #     return date.today() - self.purchase_date

def add_or_append(dict, key, value):
    if key in dict:
        dict[key].append(value)
    else:
        dict[key] = [value]
    return dict


class GameInstanceManager(models.Manager):
    def create_game_instance(self, name="Portal", system="STM", played=False, beaten=False,
                             location="STM", game_format="D", purchase_date=None,
                             finish_date=None, abandoned=False,
                             flagged=False,
                             current_time=0,
                             metacritic=0.0, user_score=0.0):
        game_instance = self.create(name=name, system=system, played=played,
                                   beaten=beaten, location=location,
                                   game_format=game_format,
                                   purchase_date=purchase_date,
                                   finish_date=finish_date, abandoned=abandoned,
                                   flagged=flagged,
                                   current_time=current_time, metacritic=metacritic,
                                   user_score=user_score)
        map_single_game_instance(game_instance.id)
        return game_instance

class GameInstance(BaseModel):
    #id = models.AutoField(primary_key=True)
    objects = GameInstanceManager()
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
    current_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    metacritic = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    user_score = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    active = models.BooleanField(default=False)
    #not a property so that it can be sorted more easily.
    # @property
    # def time_to_beat(self):
    #     if self.beaten or self.abandoned:
    #         return 0.0
    #     return self.full_time_to_beat - self.current_time

    @property
    def parent_game_id(self):
        mapping = GameToInstance.objects.all().filter(instance_id=self.id)
        if mapping.count() > 0:
            return mapping[0].game_id
        else:
            return 0

    def save(self, *args, **kwargs):
        self.name = self.name.strip(" ")
        if self.metacritic <= 0.0 or self.user_score <= 0.0:
            (self.metacritic,self.user_score) = self.calculate_metacritic()
        super(GameInstance, self).save(*args, **kwargs)

    def clean(self):
        super(GameInstance, self).clean()
        errors = {}
        print type(self.current_time)
        if self.current_time < 0.0:
            errors = add_or_append(errors,'current_time',CURRENT_TIME_NEGATIVE)
        if self.played:
            if self.current_time <= 0.0:
                errors = add_or_append(errors,'current_time',CURRENT_TIME_NOT_ALLOWED)
        else:
            if self.current_time > 0.0:
                errors = add_or_append(errors,'current_time',CURRENT_TIME_NOT_ALLOWED)
        if self.finish_date and not (self.beaten or self.abandoned):
            errors = add_or_append(errors,'finish_date',FINISH_DATE_NOT_ALLOWED)
        if self.finish_date:
            if self.finish_date < self.purchase_date:
                errors = add_or_append(errors,'finish_date',FINISH_AFTER_PURCHASE)
        if self.beaten or self.abandoned:
            if not self.played:
                errors = add_or_append(errors,'played',NOT_PLAYED)
            if self.finish_date is None:
                errors = add_or_append(errors,'finish_date',FINISH_DATE_REQUIRED)
        if len(errors.keys()) > 0:
            raise ValidationError(errors)


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
                    alt = AlternateName.create(text=name,parent_entity=self)
                    alt.save()
                    return (metacritic, user_score)
                if metacritic == -2.0 or user_score == -2.0:
                    LOGGER.warning("Found %s, not full scores", name)
                    alt = AlternateName.create(text=name,parent_entity=self)
                    alt.save()
                    return (metacritic, user_score)
            except:
                LOGGER.error("MetaCritic FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        return (-1.0,-1.0)

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
    def create(cls, name, parent_entity):
        name = cls(name=name, parent_entity=parent_entity, created_date=date.today(),modified_date=date.today())
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
