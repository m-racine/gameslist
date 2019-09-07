"""
Models.py is used to define the base entities of the gamelist apps as
well as any internal functions and methods that they need for handling
and updating their own data.
"""

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

#import datetime
import sys
from datetime import date
from datetime import datetime
#from datetime import timedelta
import logging
import traceback
from django.db import models
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404 #render,
from howlongtobeat import HowLongToBeat
from metacritic import MetaCritic
from names import gen_names, gen_metacritic_names

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

def flatten(T):
    if not isinstance(T,tuple):
        return (T,)
    elif len(T) == 0:
        return ()
    else:
        return (T[0]) + flatten(T[1:])

def flattenKEY(T):
    if not isinstance(T,tuple):
        return (T,)
    elif len(T) == 0:
        return ()
    else:
        return (T[0][0],) + flattenKEY(T[1:])

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
    """
    No_future is a validation function that checks if a given
    value is greater than the current date.
    """
    today = date.today()
    if value > today:
        raise ValidationError('Purchase_Date/finish_date cannot be in the future.')
    return True

def only_positive_or_zero(value):
    """
    only_positive_or_zero is a validation function that checks if a given
    value is a negative number.
    """
    if isinstance(value, (int, float)):
        if value < 0:
            raise ValidationError('Value cannot be negative or zero.')
    else:
        raise ValidationError('Value must be a number.')
    return True

def map_single_game_instance(game_id):
    """
    Map_single_game_instance takes a created GameInstance
    and either finds a parent Game or creates one, based on
    searching on the name of the GameInstance given.
    """
    print "map_single_game_instance"
    print game_id

    game = get_object_or_404(GameInstance, pk=game_id)
    print game.id
    mapping = GameToInstance.objects.all().filter(instance_id=game.id)
    LOGGER.debug(mapping)
    if mapping.count() > 0:
        LOGGER.debug("Mapping found for %s", game)
        if game.active:
            mapping[0].primary = True
            mapping[0].save()
        return
    else:
        try:
            filtered_names = list(AlternateName.objects.all().filter(parent_entity=game.id))
            name_list = [game.name] + filtered_names
            LOGGER.error(name_list)
            for name in name_list:
                LOGGER.debug(name)
                masters = Game.objects.filter(name=name)
                if masters.count() > 1:
                    LOGGER.debug("Too many matches for %s for %s", name, game)
                    break
                elif masters.count() == 1:
                    LOGGER.info("Creating mapping from %s to %s", game, masters[0])
                    GameToInstance.objects.create(game=masters[0],
                                                  instance=game,
                                                  primary=game.active)
                    if game.active:
                        game.set_siblings_to_inactive()
                    #g_to_i.save()
                    masters[0].update_from_children()
                    break
                else:
                    LOGGER.debug("Creating new master game for %s", game)
                    master_game = Game.objects.create_game(name=game.name,
                                                           played=game.played,
                                                           beaten=game.beaten,
                                                           purchase_date=game.purchase_date,
                                                           finish_date=game.finish_date,
                                                           abandoned=game.abandoned,
                                                           flagged=game.flagged)
                    #master_game.save()

                    LOGGER.debug("Mapping new master game %s to %s", master_game, game)
                    GameToInstance.objects.create(game=master_game,
                                                  instance=game,
                                                  primary=True)

                    #set instance to active if it is the only one for a game(and is valid)
                    if not game.active:
                        game.set_active_inactive()
                    master_game.update_from_children()
                    LOGGER.info("Added %s", master_game.name)
                    break
        except:
            LOGGER.error(sys.exc_info()[0])
            LOGGER.error(sys.exc_info()[1])
            LOGGER.error(traceback.print_tb(sys.exc_info()[2]))

def convert_date_fields(model_dict):
    """
    Takes a dictionary representing the output of a form AND
    if the form had either finish date or purchase date data,
    converts the fields in the form to those fields.
    """
    if 'purchase_date_year' in model_dict:
        try:
            model_dict['purchase_date'] = date(int(model_dict['purchase_date_year']),
                                               int(model_dict['purchase_date_month']),
                                               int(model_dict['purchase_date_day']))
        except ValueError:
            model_dict['purchase_date'] = date.today()
            LOGGER.warning("Invalid date: %d-%d-%d", int(model_dict['purchase_date_year']),
                           int(model_dict['purchase_date_month']),
                           int(model_dict['purchase_date_day']))
        finally:
            del model_dict['purchase_date_year']
            del model_dict['purchase_date_month']
            del model_dict['purchase_date_day']
    if 'finish_date_year' in model_dict:
        try:
            model_dict['finish_date'] = date(int(model_dict['finish_date_year']),
                                             int(model_dict['finish_date_month']),
                                             int(model_dict['finish_date_day']))
        except ValueError:
            model_dict['finish_date'] = date.today()
            LOGGER.warning("Invalid date: %d-%d-%d", int(model_dict['finish_date_year']),
                           int(model_dict['finish_date_month']), int(model_dict['finish_date_day']))
        finally:
            del model_dict['finish_date_year']
            del model_dict['finish_date_month']
            del model_dict['finish_date_day']
    return model_dict

class BaseModel(models.Model):
    """
    BaseModel is used to be the parent of other entities to only
    have to define created/modified date logic once, and to
    allow any entity to be flagged.
    """
    created_date = models.DateField(default=None, editable=False)
    modified_date = models.DateField(default=None, editable=False)
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
    """
    Factory class for the Game object,
    includes calling calculate priority on create.
    """
    def create_game(self, name="Portal", played=False, beaten=False,
                    purchase_date=None, finish_date=None, substantial_progress=False,
                    abandoned=False, perler=False, flagged=False,
                    priority=0, times_recommended=0, times_passed_over=0,
                    full_time_to_beat=0.0, total_time=0.0, status='O'):
        """
        Factory method for creating Game objects.
        """
        game = self.create(name=name, played=played, beaten=beaten,
                           purchase_date=purchase_date, finish_date=finish_date,
                           abandoned=abandoned, perler=perler,
                           substantial_progress=substantial_progress,
                           flagged=flagged, priority=priority, times_recommended=times_recommended,
                           times_passed_over=times_passed_over, full_time_to_beat=full_time_to_beat,
                           total_time=total_time, status=status)
        #(game.metacritic,game.user_score) = game.calculate_metacritic()
        game.priority = game.calculate_priority()
        game.save()
        return game

class Game(BaseModel):
    """
    Core entity of the gamelist app, represents
    a game as an overall entity. Owned copies of that
    game are GameInstances.
    """
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
    #calculated from child instances
    priority = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    #calculated from child instances
    substantial_progress = models.BooleanField(default=False)
    times_recommended = models.IntegerField(default=0, validators=[only_positive_or_zero])
    times_passed_over = models.IntegerField(default=0, validators=[only_positive_or_zero])
    full_time_to_beat = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    total_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    aging = models.IntegerField(default=0, validators=[only_positive_or_zero])
    play_aging = models.IntegerField(default=0, validators=[only_positive_or_zero])
    average_score = models.FloatField(default=0.0)

    @property
    def remaining_time(self):
        return self.full_time_to_beat - self.total_time

    @property
    def active_instance(self):
        try:
            return GameToInstance.objects.filter(game=self.id,primary=True)[0].instance
        except:
            return None

    def __str__(self):
        return self.name

    def __unicode__(self):
        return unicode(self.name)

    def save(self, *args, **kwargs):
        print "game save"
        self.name = self.name.strip(" ")
        #self.update_from_children()
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
        print "about to calculate"
        self.priority = self.calculate_priority()
        super(Game, self).save(*args, **kwargs)



    def update_from_children(self):
        """
        Update from childen takes the set of instances
        that map to the base Game and calculate some fields
        such as priority that depend on those instances.
        """
        print "update_from_children"
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
            #if self.active_instance:
            #    pass
            #else:
           #     instance.set_active_inactive()
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
            elif instance.game_format in ["M", "R", "E", "L", "N"]:
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
        print "score {0} and time {1}".format(self.average_score, self.total_time)

    def calculate_how_long_to_beat(self):
        """
        Calculates howlong to beat data for the entity.
        """
        print "calculate_how_long_to_beat"
        names_list = [self.name] + list(AlternateName.objects.all().filter(parent_entity=self.id))
        for name in names_list:
            try:
                if isinstance(name, AlternateName):
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
                    alt = AlternateName.create(name=name, parent_entity=self)
                    alt.save()
                    return fulltime
                elif fulltime == -1.0:
                    LOGGER.warning("Found %s, no time recorded", name)
                    alt = AlternateName.create(name=name, parent_entity=self)
                    alt.save()
                    return fulltime
            except:
                LOGGER.error("HLTB FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        return -1.0

    def calculate_priority(self):
        """
        Calculates priority based on the data both
        inherent to the Game and in its child Instances.
        """
        print "calculate_priority"
        self.update_from_children()
        try:
            if self.beaten or self.abandoned:
                return -1.0
            if self.status == "N":
                return -2.0
            score_factor = self.average_score/float(self.full_time_to_beat)
            if score_factor < 0.0:
                score_factor = 0.0
            age_factor = ((self.aging / 365.0) * 12.0) * 0.5
            rec_factor = float(1 + self.times_recommended) / float(1 + self.times_passed_over)
            LOGGER.debug("score: %2.f age: %2.f rec %2.f", score_factor, age_factor, rec_factor)
            misc_factor = 1.0
            if self.played:
                misc_factor += 1.0
            if self.status == "B":
                misc_factor += 1.0
            #if self.substantial_progress:
            #   misc_factor += 1.0
            prior = round(((age_factor +  score_factor) * misc_factor) * rec_factor, 2)
            if round(prior, 1) == 0.0:
                return -3.0
            return prior
        except:
            print sys.exc_info()[0]
            print sys.exc_info()[1]
        print "{0} age {1} rec {2} score {3} misc".format(age_factor,rec_factor,score_factor,misc_factor)
        return -4.0

def add_or_append(dic, key, value):
    """
    Given a dictionary, key and value
    Either adds the value to the dictionary as a list at that key or
    appends the value to the list already at that key.
    """
    if isinstance(key,list) or isinstance(key,dict):
        raise TypeError("Key must not be a collection.")
    if not isinstance(dic,dict):
        raise TypeError("Dic must be a dictionary.")
    if key in dic:
        dic[key].append(value)
    else:
        dic[key] = [value]
    return dic


class GameInstanceManager(models.Manager):
    """
    Factory class for the GameInstance entity.
    """
    def create_game_instance(self, name="Portal", system="STM", played=False, beaten=False,
                             location="STM", game_format="D", purchase_date=None,
                             finish_date=None, abandoned=False,
                             flagged=False,
                             current_time=0,
                             metacritic=0.0, user_score=0.0,
                             active=False):
        """
        Factory method for the GameInstance class.
        """
        game_instance = self.create(name=name, system=system, played=played,
                                    beaten=beaten, location=location,
                                    game_format=game_format,
                                    purchase_date=purchase_date,
                                    finish_date=finish_date, abandoned=abandoned,
                                    flagged=flagged,
                                    current_time=current_time, metacritic=metacritic,
                                    user_score=user_score,
                                    active=active)
        map_single_game_instance(game_instance.id)
        #game_instance.save()
        return game_instance

class GameInstance(BaseModel):
    """
    Core entity for GamesList. Represents an
    owned copy of a Game object.
    """
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
        """
        Shorthand property for returning the idea of a GameInstance's parent Game.
        """
        mapping = GameToInstance.objects.all().filter(instance_id=self.id)
        if mapping.count() > 0:
            return mapping[0].game_id
        #else:
        return 0

    def save(self, *args, **kwargs):
        print "instance save"
        self.name = self.name.strip(" ")
        if self.metacritic <= 0.0 or self.user_score <= 0.0:
            (self.metacritic, self.user_score) = self.calculate_metacritic()
        super(GameInstance, self).save(*args, **kwargs)

    def clean(self):
        super(GameInstance, self).clean()
        errors = {}
        if self.current_time < 0.0:
            errors = add_or_append(errors, 'current_time', CURRENT_TIME_NEGATIVE)
        if self.played:
            if self.current_time <= 0.0:
                errors = add_or_append(errors, 'current_time', CURRENT_TIME_NOT_ALLOWED)
        else:
            if self.current_time > 0.0:
                errors = add_or_append(errors, 'current_time', CURRENT_TIME_NOT_ALLOWED)
        if self.finish_date and not (self.beaten or self.abandoned):
            errors = add_or_append(errors, 'finish_date', FINISH_DATE_NOT_ALLOWED)
        if self.finish_date:
            if self.finish_date < self.purchase_date:
                errors = add_or_append(errors, 'finish_date', FINISH_AFTER_PURCHASE)
        if self.beaten or self.abandoned:
            if not self.played:
                errors = add_or_append(errors, 'played', NOT_PLAYED)
            if self.finish_date is None:
                errors = add_or_append(errors, 'finish_date', FINISH_DATE_REQUIRED)
        if errors.keys():
            raise ValidationError(errors)


    def calculate_metacritic(self):
        """
        Using the imported metacritic module, fetches the
        metacritic and user_score for a GameInstance
        """
        print "calculate_metacritic"
        names_list = [self.name] + list(AlternateName.objects.all().filter(parent_entity=self.id))
        for name in names_list:
            try:
                if isinstance(name, AlternateName):
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
                    alt = AlternateName.create(name=name, parent_entity=self)
                    alt.save()
                    return (metacritic, user_score)
                if metacritic == -2.0 or user_score == -2.0:
                    LOGGER.warning("Found %s, not full scores", name)
                    alt = AlternateName.create(name=name, parent_entity=self)
                    alt.save()
                    return (metacritic, user_score)
            except:
                LOGGER.error("MetaCritic FAIL FOR %s", name)
                LOGGER.error(sys.exc_info()[0])
                LOGGER.error(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
        return (-1.0, -1.0)

    def get_all_siblings(self):
        print "get_all_siblings"
        mapping = GameToInstance.objects.all().filter(instance_id=self.id)
        siblings = []
        if mapping.count() > 0:
            #insurance, a mapping should exist after all
            siblings_map = GameToInstance.objects.all().filter(game_id=mapping[0].id).exclude(instance_id=self.id)

            for sib in siblings_map:
                siblings.append(GameInstance.objects.get(pk=sib.instance_id))
        else:
            print "mapping"
            map_single_game_instance(self)
            return None
        return siblings

    def get_valid_siblings(self):
        print "get_valid_siblings"
        mapping = GameToInstance.objects.all().filter(instance_id=self.id)
        siblings = []
        if mapping.count() > 0:
            #insurance, a mapping should exist after all
            siblings_map = GameToInstance.objects.filter(game_id=mapping[0].game_id).exclude(instance_id=self.id)
            for sib in siblings_map:
                sibling = GameInstance.objects.get(pk=sib.instance_id)
                if sibling.game_format in ["M","N","L"]:
                    pass
                else:
                    siblings.append(sibling)
        else:
            #map_single_game_instance(self)
            return None
        return siblings

    def set_siblings_to_inactive(self):
        print "set_siblings_to_inactive"
        for instance in self.get_all_siblings():
            instance.active = False
            instance.save()


    def set_active_inactive(self):
        print "set_active_inactive"
        if self.active == False:
            if self.game_format in ["M","N","L"]:
                self.active = False
                self.save()
                #raise a toast?
            else:
                print "setting to true"
                self.active = True
                self.save()
                self.set_siblings_to_inactive()
        else:
            print unicode(self) + "toggling from True to False"
            self.active = False
            self.save()
#            print self.get_valid_siblings()#
#            print type(self.get_valid_siblings())
            instance = self.get_valid_siblings()
            print instance
            if instance:
                instance[0].active = True
                instance[0].save()


    def __str__(self):
        return self.name + " - " + self.system

    def __unicode__(self):
        return unicode(self.name) + u" - " + unicode(self.system)

#class GameManager(models.Manager):
#    def create_game(self):
#        game = self.create()


class GameToInstance(models.Model):
    """
    Helper Class for the relationship between games and GameInstances
    """
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    instance = models.ForeignKey(GameInstance, on_delete=models.CASCADE)
    primary = models.BooleanField(default=True)

class Wish(BaseModel):
    """
    Future Work:
    Represents a game I WISH to have.
    """
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
    """
    Class that represents a note attached to an entity.
    """
    note = models.CharField(max_length=500, default="", blank=True, null=True)
    parent_entity = models.IntegerField(default=1, null=False)
    parent_entity_type = models.IntegerField(default=1)
    def __str__(self):
        return self.note

class Flag(BaseModel):
    """
    Class representing a note that is a marker saying
    that there is an issue with a game.
    """
    is_resolved = models.BooleanField(default=False)
    resolved_date = models.DateField(default=None)
    note = models.CharField(max_length=500, default="", blank=True, null=True)
    parent_entity = models.IntegerField(default=1, null=False)
    parent_entity_type = models.IntegerField(default=1)

    def __str__(self):
        return self.note

class AlternateName(BaseModel):
    """
    Objects representing other names that a Game or its instance
    go by. Generally used for strange formatting or special editions.
    """
    parent_entity = models.IntegerField(default=1, null=False)
    name = models.CharField(max_length=200, default="", blank=True, null=True)
    parent_entity_type = models.IntegerField(default=1)

    def __str__(self):
        return self.name

    @classmethod
    def create(cls, name, parent_entity):
        """
        Basic create/init method for the AlternateName
        """
        name = cls(name=name, parent_entity=parent_entity,
                   created_date=date.today(), modified_date=date.today())
        # do something with the book
        return name

class TopPriority(BaseModel):
    id = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=3, choices=STATUSES, default="O")
    name = models.CharField(max_length=200, default="")
    played = models.BooleanField(default=False)
    beaten = models.BooleanField(default=False)
    purchase_date = models.DateField('date purchased', default=None,
                                     validators=[no_future])
    finish_date = models.DateField('date finished', default=None, blank=True, null=True,
                                   validators=[no_future])
    abandoned = models.BooleanField(default=False)
    perler = models.BooleanField(default=False)
    priority = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    substantial_progress = models.BooleanField(default=False)
    times_recommended = models.IntegerField(default=0, validators=[only_positive_or_zero])
    times_passed_over = models.IntegerField(default=0, validators=[only_positive_or_zero])
    full_time_to_beat = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    total_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    aging = models.IntegerField(default=0, validators=[only_positive_or_zero])
    play_aging = models.IntegerField(default=0, validators=[only_positive_or_zero])
    average_score = models.FloatField(default=0.0)
    #reviewd, flagged and notes_old need to be removed from the db
    system = models.CharField(max_length=3, choices=SYSTEMS, default="STM")
    location = models.CharField(max_length=3, choices=SYSTEMS, default='STM')
    game_format = models.CharField('format', max_length=1, choices=FORMATS, default='D')
    current_time = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    metacritic = models.FloatField(default=0.0, validators=[only_positive_or_zero])
    user_score = models.FloatField(default=0.0, validators=[only_positive_or_zero])

    class Meta:
        managed = False
        db_table = 'top_priority'

# class Series(BaseModel):
#     """
#     Future work: class representing a series
#     """
#     name = models.CharField(max_length=200, default="", blank=True, null=True)
#     linear = models.BooleanField(default=False)
#
# class SubSeries(Series):
#     """
#     Future work: class representing a series
#     """
#     parent_series = models.ForeignKey(Series, related_name="series_to_subseries", on_delete=models.CASCADE, null=True)
#
# class GameToSeries(models.Model):
#     """
#     Future Work: relationship table for Games and Series
#     """
#     game = models.ForeignKey(Game, on_delete=models.CASCADE, null=True)
#     series = models.ForeignKey(Series, related_name="game_to_series", on_delete=models.CASCADE, null=True)
#     subseries = models.ForeignKey(SubSeries, related_name="game_to_subseries", on_delete=models.CASCADE, null=True)

#https://schier.co/blog/2014/12/05/html-templating-output-a-grid-in-a-single-loop.html
