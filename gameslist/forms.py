"""
Contains form logic for the Gamelist app.
"""

from datetime import datetime

from django.forms import ModelForm, SelectDateWidget
from .models import Game, Note, AlternateName, GameInstance
YEARS = [x for x in range(1992, int(datetime.now().year) + 1, 1)]
YEARS.reverse()

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

class NoteForm(ModelForm):
    """
    Form for adding Notes
    """
    class Meta:
        model = Note
        fields = ('note',)

class AlternateNameForm(ModelForm):
    """
    Form for adding AlternateNames
    """
    class Meta:
        model = AlternateName
        fields = ('name',)
