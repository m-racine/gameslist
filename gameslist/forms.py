"""
Contains form logic for the Gamelist app.
"""

from datetime import datetime
from datetime import date

from django.forms import ModelForm, SelectDateWidget
from django.core.exceptions import ValidationError

from .models import Game, Note, AlternateName, GameInstance

import logging

LOGGER = logging.getLogger('forms') # pragma: no cover


YEARS = [x for x in range(1992, int(datetime.now().year) + 1, 1)]
YEARS.reverse()

CURRENT_TIME_NOT_ALLOWED = 'Current time must be 0 if a game is unplayed.'
CURRENT_TIME_NEGATIVE = 'If a game is played the current_time must be over 0.'
FINISH_DATE_NOT_ALLOWED = "finish_date must be empty if game isn't played and beaten or abandoned."
NOT_PLAYED = 'You must have played a game to beat or abandon it.'
FINISH_AFTER_PURCHASE = 'finish_date must be after date of purchase.'
FINISH_DATE_REQUIRED = 'You must have a finish date to beat or abandon a game.'
FUTURE_DATE = 'Purchase_Date/finish_date cannot be in the future.'

class GameInstanceForm(ModelForm):
#https://stackoverflow.com/questions/604266/django-set-default-form-values
    #def __init__(self, *args, **kwargs):
        #super(GameForm, self).__init__(*args, **kwargs)
        #self.initial['purchase_date'] = date.today()
        #LOGGER.debug(self.initial['purchase_date'])

    class Meta:
        model = GameInstance
        fields = ('name', 'system', 'location', 'game_format',
                  'played', 'beaten', 'abandoned',
                  'current_time', 'purchase_date', 'finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=YEARS),
            'purchase_date': SelectDateWidget(years=YEARS),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get("finish_date"):
            if cleaned_data.get("finish_date") > date.today():
                self.add_error("finish_date",FUTURE_DATE)
        if cleaned_data.get("purchase_date"):
            if cleaned_data.get("purchase_date") > date.today():
                self.add_error("purchase_date",FUTURE_DATE)

class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ('name',
                  'played', 'beaten', 'abandoned', 'perler',
                  'purchase_date', 'finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=YEARS),
            'purchase_date': SelectDateWidget(years=YEARS),
        }

    def clean(self):
        super().clean()

    #purchase_date = DateField(initial=date.today(),widget=SelectDateWidget(years=years))

    # def __init__(self, *args, **kwargs):
    #      # Get 'initial' argument if any
    #     initial_arguments = kwargs.get('initial', None)
    #     updated_initial = {}
    #     # You can also initialize form fields with hardcoded values
    #     # or perform complex DB logic here to then perform initialization
    #     updated_initial['purchase_date'] = date.today()
    #     # Finally update the kwargs initial reference
    #     kwargs.update(initial=updated_initial)
    #     super(GameForm, self).__init__(*args, **kwargs)

class PlayBeatAbandonForm(ModelForm):
    """
    Form used for setting the play status of game instances.
    """
    class Meta:
        model = GameInstance
        fields = ('played', 'current_time', 'beaten', 'abandoned', 'finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=YEARS),
        }

    def clean(self):
        super().clean()

class NoteForm(ModelForm):
    """
    Form for adding Notes
    """
    class Meta:
        model = Note
        fields = ('note',)

    def clean(self):
        super().clean()

class AlternateNameForm(ModelForm):
    """
    Form for adding AlternateNames
    """
    class Meta:
        model = AlternateName
        fields = ('name',)

    def clean(self):
        super().clean()
