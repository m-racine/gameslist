# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.shortcuts import render,get_object_or_404, reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView

from .models import Game,Wish,GameForm

# Create your views here.

#https://stackoverflow.com/questions/21153852/plotting-graphs-in-numpy-scipy

class IndexView(generic.ListView):
    template_name = 'gameslist/index.html'
    context_object_name = 'new_games_list'

    def get_queryset(self):
        return Game.objects.filter(
            purchase_date__lte=timezone.now()
        ).order_by('-purchase_date')[:5]

class GameListView(generic.ListView):
    model = Game
    template_name = 'gameslist/list.html'
    context_object_name = 'full_games_list'
    paginate_by = 10

    def get_queryset(self):
        system = self.request.GET.get('system')
        game_format = self.request.GET.get('format')
        if system and game_format:
            return Game.objects.filter(system=system).filter(game_format=game_format).order_by('name')
        elif system:
            return Game.objects.filter(system=system).order_by('name')
        elif game_format:
            return Game.objects.filter(game_format=game_format).order_by('name')
        else:
            return Game.objects.all().order_by('name')

# class GameSystemListView(generic.ListView):
#     model = Game
#     template_name = 'gameslist/list.html'
#     context_object_name = 'full_games_list'
#     paginate_by = 10

#     def get_queryset(self):
#         return Game.objects.filter(system=system).order_by('name')

# class GameListView(generic.ListView):
#     model = Game
#     template_name = 'gameslist/list.html'
#     context_object_name = 'full_games_list'
#     paginate_by = 10

#     def get_queryset(self):
#         return Game.objects.filter(system=system).order_by('name')

class DetailView(generic.DetailView):
    model = Game
    template_name = 'gameslist/detail.html'

class CreateGame(generic.CreateView):
    model = Game
    #fields = ['name']
    form_class = GameForm

    def get_success_url(self):
        return reverse('gameslist:list', args=())

#def new_game(request):
#    form = Game()
#    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))
    

def beat_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    #set game.beat to true
    game.beaten = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

def play_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    #set game.beat to true
    game.played = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

def abandon_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    #set game.beat to true
    game.abandoned = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

# def games_by_system(self):
#     system = "3DS"
#     urlparams = '?system=%s' % (system)    
#     return redirect(reverse('gameslist:by_system')+urlparams)
