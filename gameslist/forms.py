from datetime import date
from datetime import datetime

from django.forms import ModelForm, SelectDateWidget
from .models import Game

class GameForm(ModelForm):
#https://stackoverflow.com/questions/604266/django-set-default-form-values
    #def __init__(self, *args, **kwargs):
        #super(GameForm, self).__init__(*args, **kwargs)
        #self.initial['purchase_date'] = date.today()
        #LOGGER.debug(self.initial['purchase_date'])

    class Meta:
        model = Game
        years = [x for x in range(datetime.now().year - 19, datetime.now().year + 1)]
        years.reverse()
        fields = ('name', 'system', 'location', 'game_format',
                  'played', 'beaten', 'abandoned', 'perler',
                  'reviewed', 'current_time', 'purchase_date', 'finish_date',
                  'notes')
        widgets = {
            'finish_date': SelectDateWidget(years=years),
            'purchase_date': SelectDateWidget(years=years),
        }

    def __init__(self, *args, **kwargs):
         # Get 'initial' argument if any
        initial_arguments = kwargs.get('initial', None)
        updated_initial = {}
        # You can also initialize form fields with hardcoded values
        # or perform complex DB logic here to then perform initialization
        updated_initial['purchase_date'] = date.today()
        # Finally update the kwargs initial reference
        kwargs.update(initial=updated_initial)
        super(GameForm, self).__init__(*args, **kwargs)

class PlayBeatAbandonForm(ModelForm):
    class Meta:
        model = Game
        years = [x for x in range(datetime.now().year - 19, datetime.now().year + 1)]
        years.reverse()
        fields = ('played', 'current_time', 'beaten', 'abandoned', 'finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=years),
        }
