#from django.contrib.auth.models import User
import django_filters
from .models import Game, GameInstance

class GameInstanceFilter(django_filters.FilterSet):
    class Meta:
        model = GameInstance
        fields = {'name':['contains'],
                  'system':['exact'],
                  'location':['exact'],
                  'game_format':['exact'],
                  'substantial_progress':['exact'],
                  'beaten':['exact'],
                  'full_time_to_beat':['lte','gte','exact'],
                  'finish_date':['year__gte']}

class GameFilter(django_filters.FilterSet):
    class Meta:
        model = Game
        fields = {'name':['contains'],
                  'system':['exact'],
                  'location':['exact'],
                  'game_format':['exact'],
                  'substantial_progress':['exact'],
                  'beaten':['exact'],
                  'full_time_to_beat':['lte','gte','exact'],
                  'finish_date':['year__gte']}