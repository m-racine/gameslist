# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from importlib import import_module
from datetime import date, datetime, timedelta
import logging
import unittest
import os

from django.apps import apps
from django.test import TestCase
from django.test.client import Client
from django.shortcuts import reverse, get_object_or_404
from django.conf import settings
#from django.utils import timezone
from django.core.exceptions import ValidationError

from nose.plugins.attrib import attr

from howlongtobeat import HowLongToBeat

from gameslist.forms import GameInstanceForm
from gameslist.models import Game, GameInstance, GameToInstance
from gameslist.models import CURRENT_TIME_NEGATIVE, FINISH_DATE_REQUIRED, FINISH_DATE_NOT_ALLOWED
from gameslist.models import NOT_PLAYED, FINISH_AFTER_PURCHASE, CURRENT_TIME_NOT_ALLOWED
from gameslist.models import FORMATS, GAME, GAME_INSTANCE, WISH, NOTE, ALTERNATE_NAME, SERIES, SUB_SERIES, FLAG, SYSTEMS
from gameslist.models import add_or_append, convert_date_fields
from gameslist.views import check_url_args_for_only_token
from gameslist.apps import GameslistConfig
# Create your tests here.



#HOW DO I TEST admin.py
#HOW DO I TEST apps.py
logger = logging.getLogger('MYAPP')

class PersistentSessionClient(Client):
    """
    The Django test client implements the session API but doesn't persist values in it:
    https://docs.djangoproject.com/en/dev/topics/testing/?from=olddocs#django.test.client.Client.session
    This Client subclass can be used to maintain a persistent session during test cases.
    """
    #https://gist.github.com/stephenmcd/1702592
    @property
    def session(self):
        if not hasattr(self, "_persisted_session"):
            engine = import_module(settings.SESSION_ENGINE)
            self._persisted_session = engine.SessionStore("persistent")
        return self._persisted_session

def convert_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d').date()

#class WishModelTests(TestCase):

class AgingTests(unittest.TestCase):
    @attr('aging')
    def test_aging_zero(self):
        game = Game.objects.create_game(purchase_date=date.today())
        self.assertEqual(game.purchase_date, date.today())
        self.assertEqual(game.aging, 0)
        self.assertEqual(game.play_aging, 0)

    @attr('aging')
    def test_aging_over_year(self):
        game = Game.objects.create_game(played=True, beaten=True,
                           purchase_date=datetime.strptime('2016-10-30', '%Y-%m-%d'),
                           finish_date=datetime.strptime('2018-10-30', '%Y-%m-%d'))
        self.assertEqual(game.purchase_date, datetime.strptime('2016-10-30', '%Y-%m-%d'))
        self.assertEqual(game.aging, 365 + 365)
        self.assertEqual(game.play_aging, 0)

    #this is a VALID state due to preorders
    @attr('aging')
    def test_negative_aging(self):
        future_date = date.today() + timedelta(8)
        game = Game.objects.create_game(purchase_date=future_date)
        #self.assertEqual(game.purchase_date,date.today())
        self.assertEqual(game.aging, -8)
        self.assertEqual(game.play_aging, -8)

    @attr('aging')
    def test_aging_beaten(self):
        game = Game.objects.create_game(purchase_date=date.today() - timedelta(1), beaten=True,
                           finish_date=date.today(), played=True)
        self.assertGreater(game.aging, 0)
        self.assertEqual(game.play_aging, 0)
        game = Game.objects.create_game(beaten=True, played=True, purchase_date=date.today(),
                           finish_date=date.today())
        self.assertEqual(game.aging, 0)
        self.assertEqual(game.play_aging, 0)

    @attr('aging')
    def test_aging_played(self):
        game = Game.objects.create_game(played=True, purchase_date=date.today() - timedelta(1))
        self.assertEqual(game.aging, 1)
        self.assertEqual(game.play_aging, 0)

    @attr('aging')
    def test_aging_abandoned(self):
        game = Game.objects.create_game(purchase_date=date.today() - timedelta(4), abandoned=True,
                           finish_date=date.today(), played=True)
        self.assertEqual(game.aging, 4)
        self.assertEqual(game.play_aging, 0)

    @attr('aging')
    def test_aging_not_played(self):
        game = Game.objects.create_game(purchase_date=date.today() - timedelta(5))
        self.assertEqual(game.aging, 5)
        self.assertEqual(game.play_aging, 5)

class HLTBTest(TestCase):
    # @attr('hltb')
    # def test_example_hltb(self):
    #     os.chdir("gameslist/endpoints")
    #     hltb = ExampleHowLongToBeat("Sunset Overdrive")
    #     os.chdir("../../")
    #     self.assertEqual(hltb.game, "Sunset Overdrive")
    #     #print hltb
    #     self.assertEqual(hltb.fulltime, 10.0)

    @attr('hltb')
    def test_known_good_hltb(self):
        hltb = HowLongToBeat("Human Resource Machine")
        self.assertEqual(hltb.game, "Human Resource Machine")
        self.assertEqual(hltb.fulltime, 4.0)

    @attr('hltb')
    def test_known_bad_hltb(self):
        hltb = HowLongToBeat("Legion Saga")
        self.assertEqual(hltb.game, "Legion Saga")
        self.assertEqual(hltb.fulltime, -1)

    @attr('hltb')
    def test_alternate_names_hltb(self):
        hltb = HowLongToBeat("Antihero")
        self.assertEqual(str(hltb), "Antihero - Not Found")
        self.assertEqual(hltb.fulltime, -1)

        hltb = HowLongToBeat("Antihero (2017)")
        self.assertEqual(hltb.game, "Antihero (2017)")
        self.assertEqual(hltb.fulltime, 6.0)

    @attr('hltb')
    def test_full_time_on_create(self):
        game = Game.objects.create_game(name="Sunset Overdrive",purchase_date=convert_date('2018-10-01'))
        self.assertEqual(game.full_time_to_beat, 10.0)

    @attr('hltb')
    def test_time_to_beat_not_played(self):
        game = GameInstance.objects.create_game_instance(name="Sunset Overdrive", purchase_date=convert_date('2018-10-01'))
        self.assertEqual(game.current_time, 0.0)

    @attr('hltb')
    def test_time_to_beat_partial(self):
        inst = GameInstance.objects.create_game_instance(name="Sunset Overdrive", purchase_date=convert_date('2018-10-01'), current_time=4.5)
        game = Game.objects.get(pk=inst.parent_game_id)
        self.assertEqual(game.full_time_to_beat, 10.0)
        self.assertEqual(inst.current_time, 4.5)
        print game.total_time
        self.assertEqual(game.remaining_time, 5.5)

@attr('date_validation')
class GameModelTests(TestCase):

    @attr('date_validation')
    def test_past_finish_date(self):
        data = {
            'name': "Portal 2",
            #'finish_date': (2018,02,01),
            'purchase_date_day': 1,
            'purchase_date_month': 1,
            'purchase_date_year': 2018,
            'finish_date_day': 1,
            'finish_date_month': 1,
            'finish_date_year': 2017,
            'system': 'STM',
            'game_format': 'P',
            'location': 'STM',
            'played': True,
            'current_time': 2,
            'beaten': True
        }
        response = self.client.post(reverse("gameslist:add"), data)
        logger.debug(vars(response).keys())
        self.assertRaises(ValidationError({"finish_date":(FINISH_AFTER_PURCHASE)}),
                          response.context['form'].full_clean())
        logger.debug(response.context['form'])
        #self.assertTrue(False)


class ConstantTests(TestCase):
    def test_systems(self):
        self.assertTrue(('3DS', 'Nintendo 3DS') in SYSTEMS)
        self.assertTrue(('AND', 'Android') in SYSTEMS)
        self.assertTrue(('ATA', 'Atari') in SYSTEMS)
        self.assertTrue(('BNT', 'Battle.net') in SYSTEMS)
        self.assertTrue(('DIG', 'Digipen') in SYSTEMS)
        self.assertTrue(('NDS', 'Nintendo DS') in SYSTEMS)
        self.assertTrue(('EPI', 'Epic Games') in SYSTEMS)
        self.assertTrue(('GCN', 'Gamecube') in SYSTEMS)
        self.assertTrue(('GB', 'Game Boy') in SYSTEMS)
        self.assertTrue(('GBC', 'Game Boy Color') in SYSTEMS)
        self.assertTrue(('GBA', 'Game Boy Advance') in SYSTEMS)
        self.assertTrue(('GG', 'GameGear') in SYSTEMS)
        self.assertTrue(('GOG', 'GoG') in SYSTEMS)
        self.assertTrue(('HUM', 'Humble') in SYSTEMS)
        self.assertTrue(('IND', 'IndieBox') in SYSTEMS)
        self.assertTrue(('IIO', 'Itch.io') in SYSTEMS)
        self.assertTrue(('KIN', 'Kindle') in SYSTEMS)
        self.assertTrue(('NES', 'NES') in SYSTEMS)
        self.assertTrue(('N64', 'Nintendo 64') in SYSTEMS)
        self.assertTrue(('ORN', 'Origin') in SYSTEMS)
        self.assertTrue(('PC', 'PC') in SYSTEMS)
        self.assertTrue(('PSX', 'PlayStation') in SYSTEMS)
        self.assertTrue(('PS2', 'PlayStation 2') in SYSTEMS)
        self.assertTrue(('PS3', 'PlayStation 3') in SYSTEMS)
        self.assertTrue(('PS4', 'PlayStation 4') in SYSTEMS)
        self.assertTrue(('PSP', 'PlayStation Portable') in SYSTEMS)
        self.assertTrue(('SNS', 'SNES') in SYSTEMS)
        self.assertTrue(('STM', 'Steam') in SYSTEMS)
        self.assertTrue(('NSW', 'Switch') in SYSTEMS)
        self.assertTrue(('TWH', 'Twitch') in SYSTEMS)
        self.assertTrue(('UPL', 'Uplay') in SYSTEMS)
        self.assertTrue(('VIT', 'Vita') in SYSTEMS)
        self.assertTrue(('WII', 'Wii') in SYSTEMS)
        self.assertTrue(('WIU', 'Wii U') in SYSTEMS)
        self.assertTrue(('XBX', 'Xbox') in SYSTEMS)
        self.assertTrue(('360', 'Xbox 360') in SYSTEMS)
        self.assertTrue(('XB1', 'Xbox One') in SYSTEMS)

    def test_validator_messages(self):
        self.assertEqual(CURRENT_TIME_NOT_ALLOWED,'Current time must be 0 if a game is unplayed.')
        self.assertEqual(CURRENT_TIME_NEGATIVE,'If a game is played the current_time must be over 0.')
        self.assertEqual(FINISH_DATE_NOT_ALLOWED,"finish_date must be empty if game isn't played and beaten or abandoned.")
        self.assertEqual(NOT_PLAYED,'You must have played a game to beat or abandon it.')
        self.assertEqual(FINISH_AFTER_PURCHASE,'finish_date must be after date of purchase.')
        self.assertEqual(FINISH_DATE_REQUIRED,'You must have a finish date to beat or abandon a game.')

    def test_formats(self):
        self.assertTrue(("P","Physical") in FORMATS)
        self.assertTrue(('D', 'Digital') in FORMATS)
        self.assertTrue(('M', 'Missing') in FORMATS)
        self.assertTrue(('B', 'Borrowed') in FORMATS)
        self.assertTrue(('N', 'None') in FORMATS)
        self.assertTrue(('R', 'Returned') in FORMATS)
        self.assertTrue(('L', 'Lent') in FORMATS)
        self.assertTrue(('E', 'Expired') in FORMATS)
        self.assertFalse(('A','Absent') in FORMATS)

    def test_entities(self):
        self.assertEqual(GAME,1)
        self.assertEqual(GAME_INSTANCE,2)
        self.assertEqual(NOTE,3)
        self.assertEqual(ALTERNATE_NAME,4)
        self.assertEqual(WISH,5)
        self.assertEqual(SERIES,6)
        self.assertEqual(SUB_SERIES,7)
        self.assertEqual(FLAG,8)


class AddOrAppendTests(TestCase):
    def test_add_new_key_to_dict(self):
        test = add_or_append({"juice":["orange","apple"]},"soda","lemon")
        self.assertEqual(test,{"juice":["orange","apple"],"soda":["lemon"]})

    def test_add_new_value_to_array(self):
        test = add_or_append({"juice":["orange","apple"],"soda":"cola"},"juice","lemon")
        self.assertEqual(test,{"juice":["orange","apple","lemon"],"soda":"cola"})

    def test_type_exceptions(self):
        with self.assertRaises(TypeError):
            add_or_append(["orange","apple"],"soda","lemon")
        with self.assertRaises(TypeError):
            add_or_append({"juice":["orange","apple"]},["soda","water"],"lemon")

class ConvertDateFieldsTests(TestCase):
    # model_dict['purchase_date'] = date(int(model_dict['purchase_date_year']),
    #                                    int(model_dict['purchase_date_month']),
    #                                    int(model_dict['purchase_date_day']))
    def only_purchase_date_test(self):
        data = convert_date_fields({"purchase_date_year":2019,"purchase_date_day":30,"purchase_date_month":12})
        self.assertEqual(data,{"purchase_date":date(int(2019),int(12),int(30))})

    def only_finish_date_test(self):
        data = convert_date_fields({"finish_date_year":2018,"finish_date_day":7,"finish_date_month":1})
        self.assertEqual(data,{"finish_date":date(int(2018),int(1),int(7))})

    def purchase_and_finish_test(self):
        data = convert_date_fields({"purchase_date_year":2019,"purchase_date_day":30,"purchase_date_month":12,"finish_date_year":2018,"finish_date_day":7,"finish_date_month":1})
        self.assertEqual(data,{"purchase_date":date(int(2019),int(12),int(30)),"finish_date":date(int(2018),int(1),int(7))})

    def neither_purchase_or_finish_test(self):
        data = convert_date_fields({"boston":"commons","why":5})
        self.assertEqual(data, {"boston":"commons","why":5})

    def incomplete_finish_or_purchase_test(self):
        with self.assertRaises(KeyError):
            convert_date_fields({"purchase_date_year":2019,"purchase_date_day":30})

    def invalid_dates_test(self):
        #with self.assertRaises(ValueError):
        data = convert_date_fields({"purchase_date_year":2019,"purchase_date_day":32,"purchase_date_month":12})
        self.assertEqual(data,{"purchase_date":date.today()})

#NEED TO TEST PRIORITY ETC POST CREATE
#test priority is 0/negative? if all instances are inactivel

#https://github.com/django/django/blob/master/tests/modeladmin/tests.py

#fulltimetobeat of -1 and current time of 0 shouldn't equal substantial progress  (GL-72)
#need to resolve Unknown/Yes/No
#filter ignoring Substantial progress
#filter only substantial progress
#filter no substantail progress
#substantial progress = True for beaten?
