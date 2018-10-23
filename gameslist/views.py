# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date

from django.shortcuts import render
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.utils import timezone

from .models import Game,Wish

# Create your views here.

#https://stackoverflow.com/questions/21153852/plotting-graphs-in-numpy-scipy

class IndexView(generic.ListView):
    template_name = 'gameslist/index.html'
    context_object_name = 'new_games_list'

    def get_queryset(self):
        return Game.objects.filter(
            purchase_date=timezone.now()
        ).order_by('-purchase_date')[:5]

class DetailView(generic.DetailView):
    model = Game
    template_name = 'gameslist/detail.html'

    def get_queryset(self):
         """
         Excludes any questions that aren't published yet.
         """
         return Game.objects.filter(purchase_date__lte=timezone.now())



# class ResultsView(generic.DetailView):
#     model = Question
#     template_name = 'polls/results.html'


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