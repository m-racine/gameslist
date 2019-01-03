#from django.contrib.auth.models import User
import django_filters
from .models import Game

class GameFilter(django_filters.FilterSet):
    class Meta:
        model = Game
        fields = {'name':['contains'],
                  'system':['exact'],
                  'location':['exact'],
                  'game_format':['exact'],
                  #'substantial_progress':['exact'],
                  'beaten':['exact'],
                  'full_time_to_beat':['lte','gte'],
                  'finish_date':['year__gte']}