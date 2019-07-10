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
from django.core.exceptions import ValidationError

from nose.plugins.attrib import attr

from howlongtobeat import HowLongToBeat

from gameslist.forms import GameInstanceForm
from gameslist.models import Game, GameInstance
from gameslist.models import CURRENT_TIME_NEGATIVE, FINISH_DATE_REQUIRED, FINISH_DATE_NOT_ALLOWED
from gameslist.models import NOT_PLAYED, FINISH_AFTER_PURCHASE, CURRENT_TIME_NOT_ALLOWED
from gameslist.views import check_url_args_for_only_token
from gameslist.apps import GameslistConfig

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

class GameIndexViewTests(TestCase):
    def test_no_games(self):
        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available.")
        self.assertQuerysetEqual(response.context['new_games_list'], [])

    def test_new_game_in_list(self):
        Game.objects.create_game(purchase_date=convert_date('2018-10-01'))
        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        #print response.context['new_games_list']
        self.assertQuerysetEqual(response.context['new_games_list'], ['<Game: Portal>'])

    # def test_add_game(self):
    #     response = self.client.get(reverse('gameslist:add'))
    #     print response.status_code
    #     print response
    #     self.assertRedirects(response,reverse('gameslist:list'))

class GameListViewTests(TestCase):

    def test_list_filters(self):
        GameInstance.objects.create_game_instance(purchase_date=convert_date('2018-10-01'))
        GameInstance.objects.create_game_instance(name="Shin Megami Tensei IV", system="3DS",purchase_date=convert_date('2018-10-01'))
        GameInstance.objects.create_game_instance(name="Bravely Default", system="3DS", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        #template_name = 'gameslist/list.html'
        #context_object_name = 'full_games_list'
        request = self.client.get(reverse('gameslist:instance_list'))
        response = request.context['response']

        self.assertEqual(request.status_code, 200)
        print response.object_list
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Portal - STM>',
                                                        '<GameInstance: Shin Megami Tensei IV - 3DS>',
                                                        '<GameInstance: Bravely Default - 3DS>'], ordered=False)

        request = self.client.get(reverse('gameslist:instance_list'), {'system': '3DS'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Shin Megami Tensei IV - 3DS>',
                                                        '<GameInstance: Bravely Default - 3DS>'],  ordered=False)

        request = self.client.get(reverse('gameslist:instance_list'),
                                  {'system': '3DS', 'game_format': 'D'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Shin Megami Tensei IV - 3DS>'])

        request = self.client.get(reverse('gameslist:instance_list'), {'system': 'STM'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Portal - STM>'])

        request = self.client.get(reverse('gameslist:instance_list'), {'game_format': 'M'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, [])

        request = self.client.get(reverse('gameslist:instance_list'), {'system':'GBA'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, [])

        session = self.client.session
        self.assertEqual(session['query_string'], 'system=GBA')

class ListDetailRedirectTests(TestCase):
    #client_class = PersistentSessionClient
    def test_known_bad(self):
        game = GameInstance.objects.create_game_instance(name="Shin Megami Tensei IV", system="3DS", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        GameInstance.objects.create_game_instance(name="Fire Emblem", system="GBA", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        request = self.client.get(reverse('gameslist:instance_list'), follow=True)
        request = self.client.get(reverse('gameslist:detail', args=(game.id,)), follow=True)
        request = self.client.get(reverse('gameslist:instance_list'), follow=True,
                                  HTTP_REFERER="http://127.0.0.1:8000/3/")
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Fire Emblem - GBA>',
                                                        '<GameInstance: Shin Megami Tensei IV - 3DS>'],  ordered=False)
        self.assertEqual(request.status_code, 200)

    def test_list(self):
        game = GameInstance.objects.create_game_instance(name="Shin Megami Tensei IV", system="3DS", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        GameInstance.objects.create_game_instance(name="Fire Emblem", system="GBA", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        request = self.client.get(reverse('gameslist:instance_list'), {'system':'3DS'}, follow=True)
        session = self.client.session
        self.assertEqual(session['query_string'], 'system=3DS')
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Shin Megami Tensei IV - 3DS>'])

    def test_list_detail(self):
        game = GameInstance.objects.create_game_instance(name="Shin Megami Tensei IV", system="3DS", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        GameInstance.objects.create_game_instance(name="Fire Emblem", system="GBA", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        request = self.client.get(reverse('gameslist:instance_list'), {'system':'3DS'}, follow=True)
        session = self.client.session
        self.assertEqual(session['query_string'], 'system=3DS')
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Shin Megami Tensei IV - 3DS>'])
        request = self.client.get(reverse('gameslist:detail', args=(game.id,)), follow=True)
        self.assertEqual(session['query_string'], 'system=3DS')

    def test_list_detail_list(self):
        game = GameInstance.objects.create_game_instance(name="Shin Megami Tensei IV", system="3DS", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        GameInstance.objects.create_game_instance(name="Fire Emblem", system="GBA", location="3DS", game_format="P",purchase_date=convert_date('2018-10-01'))
        request = self.client.get(reverse('gameslist:instance_list'), {'system':'3DS'}, follow=True)
        session = self.client.session
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Shin Megami Tensei IV - 3DS>'])

        self.assertEqual(session['query_string'], 'system=3DS')
        request = self.client.get(reverse('gameslist:detail', args=(game.id,)), follow=True)
        self.assertEqual(session['query_string'], 'system=3DS')
        request = self.client.get(reverse('gameslist:instance_list'),
                                  HTTP_REFERER="http://127.0.0.1:8000/2/detail/", follow=True)
        #self.assertQuerysetEqual(request.context['response'].object_list,['<Game: Test - 3DS>'])
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Shin Megami Tensei IV - 3DS>'])
        self.assertEqual(session['query_string'], 'system=3DS')
        self.assertEqual(request.status_code, 200)


class GameDetailViewTests(TestCase):

    #
    def test_create_game(self):
        """
        """
        game = Game.objects.create_game(purchase_date=convert_date("2018-1-1"))
        game = get_object_or_404(Game, pk=game.id)
        self.assertEqual(game.name, "Portal")

    def test_play_game(self):
        game = GameInstance.objects.create_game_instance(finish_date=None,purchase_date=convert_date('2018-10-01'))
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
        game = GameInstance.objects.create_game_instance(purchase_date=convert_date('2018-10-01'))
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
        game = GameInstance.objects.create_game_instance(purchase_date=convert_date('2018-10-01'))
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
        game = Game.objects.create_game(purchase_date=convert_date('2018-10-01'))
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

class AddGameViewTest(TestCase):
    def test_basic_add(self):
        response = self.client.post(
            reverse('gameslist:add'), {'name':"Test",'played':True,'current_time': 1,'purchase_date_year': 2018,
            'purchase_date_month': 01,
            'purchase_date_day': 01,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM'}
        )
        request = self.client.get(reverse('gameslist:instance_list'), follow=True)
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<GameInstance: Test - STM>'])
        request = self.client.get(reverse('gameslist:list'), follow=True)
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test>'])

        # request = self.client.get(reverse('gameslist:list'), follow=True)
        # response = request.context['response']
        # self.assertQuerysetEqual(response.object_list, ['<Game: Test>'])
