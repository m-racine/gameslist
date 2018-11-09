#from django.contrib.auth.models import User
import django_filters
from .models import Game

#class UserFilter(django_filters.FilterSet):
#    class Meta:
#        model = User
#        fields = ['username', 'first_name', 'last_name', ]


class GameFilter(django_filters.FilterSet):
    class Meta:
        model = Game
        fields = ['system','game_format']