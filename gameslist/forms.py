from datetime import date
from datetime import datetime

from django.forms import ModelForm, SelectDateWidget, DateField
from .models import Game, Note, AlternateName, GameInstance

years = [x for x in range(datetime.now().year - 19, datetime.now().year + 1)]
years.reverse()

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
            'finish_date': SelectDateWidget(years=years),
            'purchase_date': SelectDateWidget(years=years),
        }


class GameForm(ModelForm):
    class Meta:
        model = Game
        fields = ('name',
                  'played', 'beaten', 'abandoned', 'perler',
                  'purchase_date', 'finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=years),
            'purchase_date': SelectDateWidget(years=years),
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
    class Meta:
        model = GameInstance
        years = [x for x in range(datetime.now().year - 19, datetime.now().year + 1)]
        years.reverse()
        fields = ('played', 'current_time', 'beaten', 'abandoned', 'finish_date')
        widgets = {
            'finish_date': SelectDateWidget(years=years),
        }

class NoteForm(ModelForm):
    class Meta:
        model = Note
        fields = ('note',)

class AlternateNameForm(ModelForm):
    class Meta:
        model = AlternateName
        fields = ('name',)
