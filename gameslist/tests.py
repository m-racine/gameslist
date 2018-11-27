# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from importlib import import_module
from datetime import date, datetime, timedelta
import logging
import unittest

from django.apps import apps
from django.test import TestCase
from django.test.client import Client
from django.shortcuts import reverse, get_object_or_404
from django.conf import settings
#from django.utils import timezone
from django.core.exceptions import ValidationError

from nose.plugins.attrib import attr

from endpoints.howlongtobeat import HowLongToBeat, ExampleHowLongToBeat

from .forms import GameForm
from .models import Game
from .models import CURRENT_TIME_NEGATIVE, FINISH_DATE_REQUIRED, FINISH_DATE_NOT_ALLOWED
from .models import NOT_PLAYED, FINISH_AFTER_PURCHASE, CURRENT_TIME_NOT_ALLOWED
from .views import check_url_args_for_only_token
from .apps import GameslistConfig
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

def create_game(name="Test", system="STM", played=False, beaten=False, location="STM",
                game_format="D", notes="",
                purchase_date=datetime.strptime('2018-10-30', '%Y-%m-%d'),
                finish_date=datetime.strptime('2018-10-30', '%Y-%m-%d'),
                abandoned=False, perler=False, reviewed=False, flagged=False, current_time=0):
    return Game.objects.create(name=name, system=system, played=played, beaten=beaten,
                               location=location, game_format=game_format, notes=notes,
                               purchase_date=purchase_date, finish_date=finish_date,
                               abandoned=abandoned, perler=perler, reviewed=reviewed,
                               flagged=flagged, current_time=current_time)

def convert_date(date_string):
    return datetime.strptime(date_string, '%Y-%m-%d').date()

#class WishModelTests(TestCase):

class AgingTests(unittest.TestCase):
    @attr('aging')
    def test_aging_zero(self):
        game = create_game(purchase_date=date.today())
        self.assertEqual(game.purchase_date, date.today())
        self.assertEqual(game.aging.days, 0)
        self.assertEqual(game.play_aging.days, 0)

    @attr('aging')
    def test_aging_over_year(self):
        game = create_game(played=True, beaten=True,
                           purchase_date=datetime.strptime('2016-10-30', '%Y-%m-%d'),
                           finish_date=datetime.strptime('2018-10-30', '%Y-%m-%d'))
        self.assertEqual(game.purchase_date, datetime.strptime('2016-10-30', '%Y-%m-%d'))
        self.assertEqual(game.aging.days, 365 + 365)
        self.assertEqual(game.play_aging.days, 0)

    #this is a VALID state due to preorders
    @attr('aging')
    def test_negative_aging(self):
        future_date = date.today() + timedelta(8)
        game = create_game(purchase_date=future_date)
        #self.assertEqual(game.purchase_date,date.today())
        self.assertEqual(game.aging.days, -8)
        self.assertEqual(game.play_aging.days, -8)

    @attr('aging')
    def test_aging_beaten(self):
        game = create_game(purchase_date=date.today() - timedelta(1), beaten=True,
                           finish_date=date.today(), played=True)
        self.assertGreater(game.aging.days, 0)
        self.assertEqual(game.play_aging.days, 0)
        game = create_game(beaten=True, played=True, purchase_date=date.today(),
                           finish_date=date.today())
        self.assertEqual(game.aging.days, 0)
        self.assertEqual(game.play_aging.days, 0)

    @attr('aging')
    def test_aging_played(self):
        game = create_game(played=True, purchase_date=date.today() - timedelta(1))
        self.assertEqual(game.aging.days, 1)
        self.assertEqual(game.play_aging.days, 0)

    @attr('aging')
    def test_aging_abandoned(self):
        game = create_game(purchase_date=date.today() - timedelta(4), abandoned=True,
                           finish_date=date.today(), played=True)
        self.assertEqual(game.aging.days, 4)
        self.assertEqual(game.play_aging.days, 0)

    @attr('aging')
    def test_aging_not_played(self):
        game = create_game(purchase_date=date.today() - timedelta(5))
        self.assertEqual(game.aging.days, 5)
        self.assertEqual(game.play_aging.days, 5)

class GameIndexViewTests(TestCase):
    def test_no_games(self):
        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available.")
        self.assertQuerysetEqual(response.context['new_games_list'], [])

    def test_new_game_in_list(self):
        create_game()
        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        #print response.context['new_games_list']
        self.assertQuerysetEqual(response.context['new_games_list'], ['<Game: Test - STM>'])

    # def test_add_game(self):
    #     response = self.client.get(reverse('gameslist:add'))
    #     print response.status_code
    #     print response
    #     self.assertRedirects(response,reverse('gameslist:list'))

class GameListViewTests(TestCase):

    def test_list_filters(self):
        create_game()
        create_game("Test 2", "3DS")
        create_game("Test 3", "3DS", False, False, "3DS", "P")
        #template_name = 'gameslist/list.html'
        #context_object_name = 'full_games_list'
        request = self.client.get(reverse('gameslist:list'))
        response = request.context['response']

        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - STM>',
                                                        '<Game: Test 2 - 3DS>',
                                                        '<Game: Test 3 - 3DS>'])

        request = self.client.get(reverse('gameslist:list'), {'system': '3DS'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test 2 - 3DS>',
                                                        '<Game: Test 3 - 3DS>'])

        request = self.client.get(reverse('gameslist:list'),
                                  {'system': '3DS', 'game_format': 'D'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test 2 - 3DS>'])

        request = self.client.get(reverse('gameslist:list'), {'system': 'STM'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - STM>'])

        request = self.client.get(reverse('gameslist:list'), {'game_format': 'M'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, [])

        request = self.client.get(reverse('gameslist:list'), {'system':'GBA'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, [])

        session = self.client.session
        self.assertEqual(session['query_string'], 'system=GBA')

class ListDetailRedirectTests(TestCase):
    #client_class = PersistentSessionClient
    def test_known_bad(self):
        game = create_game("Test", "3DS", False, False, "3DS", "P")
        create_game("Test 2", "GBA", False, False, "3DS", "P")
        request = self.client.get(reverse('gameslist:list'), follow=True)
        request = self.client.get(reverse('gameslist:detail', args=(game.id,)), follow=True)
        request = self.client.get(reverse('gameslist:list'), follow=True,
                                  HTTP_REFERER="http://127.0.0.1:8000/3/")
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>',
                                                        '<Game: Test 2 - GBA>'])
        self.assertEqual(request.status_code, 200)

    def test_list(self):
        create_game("Test", "3DS", False, False, "3DS", "P")
        create_game("Test 2", "GBA", False, False, "3DS", "P")
        request = self.client.get(reverse('gameslist:list'), {'system':'3DS'}, follow=True)
        session = self.client.session
        self.assertEqual(session['query_string'], 'system=3DS')
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])

    def test_list_detail(self):
        game = create_game("Test", "3DS", False, False, "3DS", "P")
        create_game("Test 2", "GBA", False, False, "3DS", "P")
        request = self.client.get(reverse('gameslist:list'), {'system':'3DS'}, follow=True)
        session = self.client.session
        self.assertEqual(session['query_string'], 'system=3DS')
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])
        request = self.client.get(reverse('gameslist:detail', args=(game.id,)), follow=True)
        self.assertEqual(session['query_string'], 'system=3DS')

    def test_list_detail_list(self):
        game = create_game("Test", "3DS", False, False, "3DS", "P")
        create_game("Test 2", "GBA", False, False, "3DS", "P")
        request = self.client.get(reverse('gameslist:list'), {'system':'3DS'}, follow=True)
        session = self.client.session
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])

        self.assertEqual(session['query_string'], 'system=3DS')
        request = self.client.get(reverse('gameslist:detail', args=(game.id,)), follow=True)
        self.assertEqual(session['query_string'], 'system=3DS')
        request = self.client.get(reverse('gameslist:list'),
                                  HTTP_REFERER="http://127.0.0.1:8000/3/", follow=True)
        #self.assertQuerysetEqual(request.context['response'].object_list,['<Game: Test - 3DS>'])
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])
        self.assertEqual(session['query_string'], 'system=3DS')
        self.assertEqual(request.status_code, 200)


class GameDetailViewTests(TestCase):

    #
    def test_create_game(self):
        """
        """
        game = create_game()
        game = get_object_or_404(Game, pk=game.id)
        self.assertEqual(game.name, "Test")

    def test_play_game(self):
        game = create_game(finish_date=None)
        self.assertFalse(game.played)
        response = self.client.post(
            reverse('gameslist:play_game', kwargs={'pk':game.id}),
            {'played':True,
             'current_time': 1}
        )
        self.assertEqual(response.status_code, 302)
        game.refresh_from_db()
        self.assertTrue(game.played)


    def test_beat_game(self):
        game = create_game()
        self.assertFalse(game.beaten)
        response = self.client.post(
            reverse('gameslist:play_game', kwargs={'pk':game.id}),
            {'played':True,
             'current_time':1,
             'beaten':True,
             'finish_date_year': 2018,
             'finish_date_day':1,
             'finish_date_month': 11}
        )
        self.assertEqual(response.status_code, 302)
        game.refresh_from_db()
        self.assertTrue(game.beaten)

    def test_abandon_game(self):
        #play_game
        game = create_game()
        self.assertFalse(game.abandoned)
        response = self.client.post(
            reverse('gameslist:play_game', kwargs={'pk':game.id}),
            {'finish_date_year': 2018,
             'finish_date_day':1,
             'finish_date_month': 11,
             'played':True,
             'current_time':1,
             'abandoned':True}
        )
        self.assertEqual(response.status_code, 302)
        game.refresh_from_db()
        self.assertTrue(game.abandoned)

    def test_flag_game(self):
        game = create_game()
        self.assertFalse(game.flagged)
        _ = self.client.post(reverse('gameslist:flag_game', args=(game.id,)))
        game = get_object_or_404(Game, pk=game.id)
        self.assertEqual(game.flagged, True)

class GameslistConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(GameslistConfig.name, 'gameslist')
        self.assertEqual(apps.get_app_config('gameslist').name, 'gameslist')

    def basic_session_test(self):
        _ = self.client.get(reverse('gameslist:list'))
        session = self.client.session
        #my_car = session['my_car']
        session['my_car'] = 'mini'
        # Get a session value, setting a default if it is not present ('mini')
        my_car = session.get('my_car', 'mini')

        # Set a session value
        print my_car
        self.assertEqual(session['my_car'], 'mini')
        # Delete a session value
        #del request.session['my_car']

class ListURLHelperTest(TestCase):

    def test_check_url_args_for_token(self):
        self.assertTrue(check_url_args_for_only_token(" "))
        self.assertTrue(check_url_args_for_only_token("/"))
        self.assertTrue(check_url_args_for_only_token("?"))
        self.assertTrue(check_url_args_for_only_token("csrfmiddlewaretoken=xxxyyy22233345455sdf"))
        self.assertFalse(check_url_args_for_only_token("csrfmiddlewaretoken=xxxyyy22233345&page=1"))


class HLTBTest(TestCase):
    @attr('hltb')
    def test_example_hltb(self):
        hltb = ExampleHowLongToBeat("Sunset Overdrive")
        self.assertEqual(hltb.game, "Sunset Overdrive")
        #print hltb
        self.assertEqual(hltb.fulltime, 10.0)

    @attr('hltb')
    def test_known_good_hltb(self):
        hltb = HowLongToBeat("Human Resource Machine")
        self.assertEqual(hltb.game, "Human Resource Machine")
        self.assertEqual(hltb.fulltime, 4.5)

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
        game = create_game("Sunset Overdrive")
        self.assertEqual(game.full_time_to_beat, 10.0)

    @attr('hltb')
    def test_time_to_beat_not_played(self):
        game = create_game("Sunset Overdrive", current_time=0)
        self.assertEqual(game.time_to_beat, 10.0)

    @attr('hltb')
    def test_time_to_beat_partial(self):
        game = create_game("Sunset Overdrive", current_time=5.5)
        self.assertEqual(game.full_time_to_beat, 10.0)
        self.assertEqual(game.time_to_beat, 4.5)

@attr('date_validation')
class GameModelTests(TestCase):
    @attr('date_validation')
    def test_future_purchase_date(self):

        form = GameForm({
            'name': "Test Future Purchase",
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM'
        })
        print form.errors.as_json()
        #self.assertTrue(convert_date(form.data['purchase_date']) > date.today())
        self.assertRaises(ValidationError('Purchase_Date/finish_date cannot be in the future.'),
                          form.full_clean())

    @attr('date_validation')
    def test_past_purchase_date(self):
        form = GameForm({
            'name': "Test Past Purchase",
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'current_time': 0
        })
        print form.errors.as_json()
        self.assertTrue(form.is_valid())

    @attr('date_validation')
    def test_future_finish_date(self):
        form = GameForm({
            'name': "Test Future Finish",
            'finish_date_year': 2019,
            'finish_date_month': 01,
            'finish_date_day': 01,
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': True,
            'beaten': True,
            'current_time': 1.0
        })
        #self.assertTrue(convert_date(form.data['finish_date']) > date.today())
        self.assertRaises(ValidationError('Purchase_Date/finish_date cannot be in the future.'),
                          form.full_clean())

    @attr('date_validation')
    def test_past_finish_date(self):
        data = {
            'name': "Test Past Finish",
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
        self.assertRaises(ValidationError({"finish_date":(FINISH_AFTER_PURCHASE)}),
                          response.context_data['form'].full_clean())
        
    @attr('date_validation')
    def test_not_played(self):
        form = GameForm({
            'name': "Test Past Finish",
            'finish_date_year': 2018,
            'finish_date_month': 01,
            'finish_date_day': 01,
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': False,
            'current_time': 0.0
        })
        print form.errors.as_json()
        #self.assertFalse(form.is_valid())
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError({'finish_date':(FINISH_DATE_NOT_ALLOWED)}),
                          form.full_clean())

    @attr('date_validation')
    def test_not_played_but_beaten(self):
        form = GameForm({
            'name': "Test Past Finish",
            'finish_date_year': 2018,
            'finish_date_month': 01,
            'finish_date_day': 01,
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': False,
            'beaten': True
        })
        print form.errors.as_json()
        #self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError({'played': (NOT_PLAYED)}),
                          form.full_clean())

    @attr('date_validation')
    def test_not_played_but_abandoned(self):
        form = GameForm({
            'name': "Test Past Finish",
            'finish_date_year': 2018,
            'finish_date_month': 01,
            'finish_date_day': 01,
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': False,
            'abandoned': True
        })
        print form.errors.as_json()
        #self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError({'played': (NOT_PLAYED)}),
                          form.full_clean())

    @attr('date_validation')
    def test_not_beaten_or_abandoned(self):
        form = GameForm({
            'name': "Test Past Finish",
            'finish_date_year': 2018,
            'finish_date_month': 01,
            'finish_date_day': 01,
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': True,
            'current_time': 1,
            'beaten': False,
            'abandoned': False
        })
        print form.errors.as_json()
        #self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError({'finish_date':(FINISH_DATE_NOT_ALLOWED)}),
                          form.full_clean())

    @attr('date_validation')
    def test_beaten_no_finish(self):
        form = GameForm({
            'name': "Test No Finish",
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': True,
            'current_time': 1,
            'beaten': True,
            'abandoned': False
        })
        print form.errors.as_json()
        #self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError({'finish_date': (FINISH_DATE_REQUIRED)}),
                          form.full_clean())
        self.assertFalse(form.is_valid())

class CurrentTimeTests(TestCase):
    #test that setting current time under 0 is impossible
    @attr('current_time')
    def test_negative_current_time(self):
        form = GameForm({
            'name': "Test Future Purchase",
            'purchase_date_year': 2018,
            'purchase_date_month': 1,
            'purchase_date_day': 1,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'current_time': -1,
            'played': True
        })
        self.assertRaises(ValidationError('Value cannot be negative or zero.'))
        self.assertRaises(ValidationError({"current_time":(CURRENT_TIME_NEGATIVE)}),
                          form.full_clean())

    #test that setting current time over 1 with played false is impossible
    @attr('current_time')
    def test_current_time_not_played(self):
        form = GameForm({
            'name': "Test Future Purchase",
            'purchase_date_year': 2018,
            'purchase_date_month': 1,
            'purchase_date_day': 1,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'current_time': 1
        })
        self.assertRaises(ValidationError({'current_time':(CURRENT_TIME_NOT_ALLOWED)}),
                          form.full_clean())

    #test that setting played to true with current time == 0 is impossible
    @attr('current_time')
    def test_no_time_yes_played(self):
        form = GameForm({
            'name': "Test Future Purchase",
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': True
        })
        print form.errors.as_json()
        self.assertRaises(ValidationError({'current_time':(CURRENT_TIME_NEGATIVE)}),
                          form.full_clean())

    #test that setting played to true AND current time > 0 is POSSIBLE
    @attr('current_time')
    def test_valid_current_played(self):
        form = GameForm({
            'name': "Test Future Purchase",
            'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': True,
            'current_time': 1
        })
        print form.errors.as_json()
        self.assertTrue(form.is_valid())
        game = form.save()
        logger.debug(form.errors.as_json())
        self.assertTrue(game.played)
        self.assertEqual(game.current_time, 1)

#https://github.com/django/django/blob/master/tests/modeladmin/tests.py
