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
from gameslist.models import Game, GameInstance
from gameslist.models import CURRENT_TIME_NEGATIVE, FINISH_DATE_REQUIRED, FINISH_DATE_NOT_ALLOWED
from gameslist.models import NOT_PLAYED, FINISH_AFTER_PURCHASE, CURRENT_TIME_NOT_ALLOWED
from gameslist.views import check_url_args_for_only_token
from gameslist.apps import GameslistConfig
# Create your tests here.

CURRENT_TIME_NOT_ALLOWED = 'Current time must be 0 if a game is unplayed.'
CURRENT_TIME_NEGATIVE = 'If a game is played the current_time must be over 0.'
FINISH_DATE_NOT_ALLOWED = "finish_date must be empty if game isn't played and beaten or abandoned."
NOT_PLAYED = 'You must have played a game to beat or abandon it.'
FINISH_AFTER_PURCHASE = 'finish_date must be after date of purchase.'
FINISH_DATE_REQUIRED = 'You must have a finish date to beat or abandon a game.'
FUTURE_DATE = 'Purchase_Date/finish_date cannot be in the future.'

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



class GameInstanceFormTests(TestCase):
    @attr('date_validation')
    def test_past_purchase_date(self):
        form = GameInstanceForm({
            'name': "Portal 2",
            'purchase_date_year': 2018,
            'purchase_date_month': 1,
            'purchase_date_day': 1,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': False,
            'current_time': 0.0
        })
        print(form.errors.as_json())
        self.assertTrue(form.is_valid())

    @attr('date_validation')
    def test_future_purchase_date(self):

        form = GameInstanceForm({
            'name': "Portal 2",
            'purchase_date_year': 2100,
            'purchase_date_month': 1,
            'purchase_date_day': 1,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'current_time': 0.0
        })
        print(form.errors.as_json())
        #self.assertTrue(convert_date(form.data['purchase_date']) > date.today())
        self.assertEqual(form.errors.get("purchase_date"),[FUTURE_DATE])
    
    @attr('date_validation')
    def test_future_finish_date(self):
        form = GameInstanceForm({
            'name': "Portal 2",
            'finish_date_year': 2100,
            'finish_date_month': 1,
            'finish_date_day': 1,
            'purchase_date_year': 2018,
            'purchase_date_month': 1,
            'purchase_date_day': 1,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': True,
            'beaten': False,
            'current_time': 1.0
        })
        #self.assertTrue(convert_date(form.data['finish_date']) > date.today())
        # with self.assertRaises(SomeException) as cm:
        #     do_something()
        # err = cm.exception
        # self.assertEqual(str(err), 'expected error message.')
        #https://github.com/cloudant/python-cloudant/issues/80
        
       # with self.assertRaises(ValidationError) as err:
        #form.full_clean()
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors.get("finish_date"),[FUTURE_DATE])

    @attr('date_validation')
    def test_not_played(self):
        form = GameInstanceForm({
            'name': "Portal 2",
            'finish_date_year': 2018,
            'finish_date_month': 1,
            'finish_date_day': 1,
            'purchase_date_year': 2018,
            'purchase_date_month': 1,
            'purchase_date_day': 1,
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM',
            'played': False,
            'current_time': 0.0
        })
        print(form.errors.as_json())
        #self.assertFalse(form.is_valid())
        self.assertFalse(form.is_valid())
        self.assertRaises(ValidationError,
                          form.full_clean()) 
