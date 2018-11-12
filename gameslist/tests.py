# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import apps
from django.test import TestCase
from django.shortcuts import reverse,get_object_or_404
from .models import Game
from .views import play_game
from .apps import GameslistConfig
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
    def test_new_game_in_list(self):
        game = create_game()

        response = self.client.get(reverse('gameslist:index'))
        self.assertEqual(response.status_code, 200)
        #print response.context['new_games_list']
        self.assertQuerysetEqual(response.context['new_games_list'], ['<Game: Test - STM>'])
    
    # def test_add_game(self):
    #     response = self.client.get(reverse('gameslist:add'))
    #     print response.status_code
    #     print response
    #     self.assertRedirects(response,reverse('gameslist:list'))

class GameListViewTests(TestCase):
    def test_list_filters(self):
        create_game()
        create_game("Test 2","3DS")
        create_game("Test 3","3DS",False,False,"3DS","P")
        #template_name = 'gameslist/list.html'
        #context_object_name = 'full_games_list'
        request = self.client.get(reverse('gameslist:list'))
        response = request.context['response']

        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - STM>','<Game: Test 2 - 3DS>','<Game: Test 3 - 3DS>'])

        request = self.client.get(reverse('gameslist:list'),{'system': '3DS'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test 2 - 3DS>','<Game: Test 3 - 3DS>'])

        request = self.client.get(reverse('gameslist:list'),{'system': '3DS','game_format': 'D'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test 2 - 3DS>'])

        request = self.client.get(reverse('gameslist:list'),{'system': 'STM'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - STM>'])

        request = self.client.get(reverse('gameslist:list'),{'game_format': 'M'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, [])

        request = self.client.get(reverse('gameslist:list'),{'system':'GBA'})
        response = request.context['response']
        self.assertEqual(request.status_code, 200)
        self.assertQuerysetEqual(response.object_list, [])

        session = self.client.session
        self.assertEqual(session['query_string'],'system=GBA')


class GameDetailViewTests(TestCase):
    def test_create_game(self):
        """
        """
        game = create_game()
        game = get_object_or_404(Game,pk=game.id)
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


class GameslistConfigTest(TestCase):
    def test_apps(self):
        self.assertEqual(GameslistConfig.name, 'gameslist')
        self.assertEqual(apps.get_app_config('gameslist').name, 'gameslist')
        
    def basic_session_test(self):
        #<td><a href={% url 'gameslist:detail' game.id page={{page_obj.current_page_number}} %}>{{ game.name }}</td>
        # Get a session value by its key (e.g. 'my_car'), raising a KeyError if the key is not present
        response = self.client.get(reverse('gameslist:list'))
        session = self.client.session
        #my_car = session['my_car']
        session['my_car'] = 'mini'
        # Get a session value, setting a default if it is not present ('mini')
        my_car = session.get('my_car', 'mini')

        # Set a session value
        print my_car
        self.assertEqual(session['my_car'],'mini')
        # Delete a session value
        #del request.session['my_car']





#https://github.com/django/django/blob/master/tests/modeladmin/tests.py