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
        return Game.objects.all()

# class UserListView(ListView):
#     model = User
#     template_name = 'core/user_list.html'  # Default: <app_label>/<model_name>_list.html
#     context_object_name = 'users'  # Default: object_list
#     paginate_by = 10
#     queryset = User.objects.all()  # Default: Model.objects.all()

class DetailView(generic.DetailView):
    model = Game
    template_name = 'gameslist/detail.html'

    def get_queryset(self):
         """
         Excludes any questions that aren't published yet.
         """
         return Game.objects.filter(purchase_date__lte=timezone.now())

class CreateGame(generic.CreateView):
    model = Game
    #fields = ['name']
    form_class = GameForm

    def get_success_url(self):
        return reverse('gameslist:index', args=())

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
# def vote(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     try:
#         selected_choice = question.choice_set.get(pk=request.POST['choice'])
#     except (KeyError, Choice.DoesNotExist):
#         # Redisplay the question voting form.
#         return render(request, 'polls/detail.html', {
#             'question': question,
#             'error_message': "You didn't select a choice.",
#         })
#     else:
#         selected_choice.votes += 1
#         selected_choice.save()
#         # Always return an HttpResponseRedirect after successfully dealing
#         # with POST data. This prevents data from being posted twice if a
#         # user hits the Back button.
#         return HttpResponseRedirect(reverse('polls:results', args=(question.id,)))