# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase
from django.shortcuts import reverse,get_object_or_404
from .models import Game
from .views import play_game
# Create your tests here.

#HOW DO I TEST admin.py
#HOW DO I TEST apps.py


def create_game(name="Test",system="STM",played=False,beaten=False,location="STM",
                game_format="D",notes="",purchase_date='2018-10-30',finish_date='2018-10-30',
                abandoned=False,perler=False,reviewed=False,flagged=False,
                aging=0,play_aging=0):
    return Game.objects.create(name=name,system=system,played=played,beaten=beaten,
                               location=location,game_format=game_format,notes=notes,
                               purchase_date=purchase_date,finish_date=finish_date,
                               abandoned=abandoned,perler=perler,reviewed=reviewed,flagged=flagged,
                               aging=aging,play_aging=play_aging)

#class WishModelTests(TestCase):

class GameIndexViewTests(TestCase):
    def test_no_games(self):
        """
        If no questions exist, an appropriate message is displayed.
        """
        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No games are available.")
        self.assertQuerysetEqual(response.context['new_games_list'], [])

class GameDetailViewTests(TestCase):
    def test_create_game(self):
        """
        """
        game = create_game()

        self.assertEqual(game.name,"Test")

    def test_play_game(self):
        game = create_game()
        # <form action="{% url 'gameslist:beat_game' game.id %}" method="post">
        #         {% csrf_token %}
        #         <button type="submit"> Beat!</button>
        #     </form> 
        response = self.client.post(reverse('gameslist:play_game',args=(game.id,)))

        #print response.content
        #print response.reason_phrase
        #self.assertEqual(response.status_code,200)
        #play_game(game.id)
        game = get_object_or_404(Game,pk=game.id)
        self.assertEqual(game.played,True)


    def test_beat_game(self):
        game = create_game()
        response = self.client.post(reverse('gameslist:beat_game',args=(game.id,)))
        game = get_object_or_404(Game,pk=game.id)
        self.assertEqual(game.beaten,True)

    def test_abandon_game(self):
        game = create_game()
        response = self.client.post(reverse('gameslist:abandon_game',args=(game.id,)))
        game = get_object_or_404(Game,pk=game.id)
        self.assertEqual(game.abandoned,True)    

    def test_flag_game(self):
        game = create_game()
        response = self.client.post(reverse('gameslist:flag_game',args=(game.id,)))
        game = get_object_or_404(Game,pk=game.id)
        self.assertEqual(game.flagged,True)


#         <form action="{% url 'gameslist:add'%}" method="post">
#     {% csrf_token %}
#     <button type="submit">Add New Game</button>
# </form> 