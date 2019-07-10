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

from gameslist.forms import GameInstanceForm
from gameslist.models import Game, GameInstance
from gameslist.models import no_future, only_positive_or_zero
from gameslist.models import CURRENT_TIME_NEGATIVE, FINISH_DATE_REQUIRED, FINISH_DATE_NOT_ALLOWED
from gameslist.models import NOT_PLAYED, FINISH_AFTER_PURCHASE, CURRENT_TIME_NOT_ALLOWED

# CURRENT_TIME_NOT_ALLOWED = 'Current time must be 0 if a game is unplayed.'
# CURRENT_TIME_NEGATIVE = 'If a game is played the current_time must be over 0.'
# FINISH_DATE_NOT_ALLOWED = "finish_date must be empty if game isn't played and beaten or abandoned."
# NOT_PLAYED = 'You must have played a game to beat or abandon it.'
# FINISH_AFTER_PURCHASE = 'finish_date must be after date of purchase.'
# FINISH_DATE_REQUIRED = 'You must have a finish date to beat or abandon a game.'

def create_game_instance(name="Portal", system="STM", played=False, beaten=False,
                         location="STM", game_format="D", purchase_date=None,
                         finish_date=None, abandoned=False,
                         flagged=False,
                         current_time=0,
                         metacritic=0.0, user_score=0.0):
    return GameInstance.objects.create(name=name, system=system, played=played,
                               beaten=beaten, location=location,
                               game_format=game_format,
                               purchase_date=purchase_date,
                               finish_date=finish_date, abandoned=abandoned,
                               flagged=flagged,
                               current_time=current_time, metacritic=metacritic,
                               user_score=user_score)

class CleanValidatorsTests(TestCase):
    def test_current_time_negative_but_played(self):
        instance = create_game_instance(current_time=-1.0,played=True,purchase_date=date.today())
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_current_time_zero_but_played(self):
        instance = create_game_instance(current_time=0.0,played=True,purchase_date=date.today())
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_current_time_positive_but_not_played(self):
        instance = create_game_instance(current_time=10.0,played=False,purchase_date=date.today())
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_finish_date_but_not_beaten_or_abandoned(self):
        instance = create_game_instance(current_time=10.0,played=True,purchase_date=date.today()-timedelta(1),finish_date=date.today())
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_finish_date_but_not_played(self):
        instance = create_game_instance(current_time=1.0,played=False,purchase_date=date.today()-timedelta(1),finish_date=date.today())
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_finish_before_purchase(self):
        instance = create_game_instance(current_time=1.0,played=True,beaten=True,purchase_date=date.today()-timedelta(1),finish_date=date.today()-timedelta(2))
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_finished_but_not_played(self):
        instance = create_game_instance(current_time=1.0,played=False,beaten=True,purchase_date=date.today()-timedelta(1),finish_date=date.today())
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_finished_but_no_date(self):
        instance = create_game_instance(current_time=1.0,played=True,purchase_date=date.today()-timedelta(1),beaten=True)
        with self.assertRaises(ValidationError):
            instance.clean()

    def test_valid_clean(self):
        instance = create_game_instance(current_time=1.0,played=True,beaten=True,purchase_date=date.today()-timedelta(1),finish_date=date.today())
        instance.clean()
        instance = create_game_instance(current_time=1.0,played=True,purchase_date=date.today()-timedelta(1),)
        instance.clean()



class NoFutureTests(TestCase):
    today = date.today()
    def test_past_date(self):
        past = self.today - timedelta(4)
        self.assertEqual(no_future(past), True)

    def test_non_date(self):
        self.assertRaises(TypeError,no_future,"Life")

    def test_same_date(self):
        self.assertEqual(no_future(self.today), True)

    def test_future_date(self):
        future = self.today + timedelta(4)
        self.assertRaises(ValidationError,no_future,future)

class OnlyPositiveOrZeroTests(TestCase):
    def test_positive_int(self):
        self.assertTrue(only_positive_or_zero(4))

    def test_zero_int(self):
        self.assertTrue(only_positive_or_zero(0))

    def test_negative_int(self):
        self.assertRaises(ValidationError, only_positive_or_zero, -7)

    def test_positive_float(self):
        self.assertTrue(only_positive_or_zero(4.6))

    def test_zero_float(self):
        self.assertTrue(only_positive_or_zero(0.0))

    def test_negative_float(self):
        self.assertRaises(ValidationError, only_positive_or_zero, -781.5122)

    def test_non_number(self):
        self.assertRaises(ValidationError, only_positive_or_zero, "Life")
