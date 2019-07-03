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

from .forms import GameInstanceForm
from .models import Game, GameInstance
from .models import CURRENT_TIME_NEGATIVE, FINISH_DATE_REQUIRED, FINISH_DATE_NOT_ALLOWED
from .models import NOT_PLAYED, FINISH_AFTER_PURCHASE, CURRENT_TIME_NOT_ALLOWED
