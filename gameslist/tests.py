# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from importlib import import_module
from datetime import date,datetime,timedelta
import logging
import unittest

from django.apps import apps
from django.test import TestCase, tag
from django.test.client import Client
from django.shortcuts import reverse,get_object_or_404
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError


from .models import Game,GameForm
from .views import play_game,check_url_args_for_only_token
from .apps import GameslistConfig
from endpoints.howlongtobeat import HowLongToBeat,ExampleHowLongToBeat
# Create your tests here.



#HOW DO I TEST admin.py
#HOW DO I TEST apps.py
#Test going to detail for a game not in the current query set.
"""
The Django test client implements the session API but doesn't persist values in it:
https://docs.djangoproject.com/en/dev/topics/testing/?from=olddocs#django.test.client.Client.session
This Client subclass can be used to maintain a persistent session during test cases.
"""
logger = logging.getLogger('MYAPP')

class PersistentSessionClient(Client):
    #https://gist.github.com/stephenmcd/1702592
    @property
    def session(self):
        if not hasattr(self, "_persisted_session"):
            engine = import_module(settings.SESSION_ENGINE)
            self._persisted_session = engine.SessionStore("persistent")
        return self._persisted_session


#class MyTests(TestCase):

#    client_class = PersistentSessionClient


def create_game(name="Test",system="STM",played=False,beaten=False,location="STM",
                game_format="D",notes="",purchase_date=datetime.strptime('2018-10-30','%Y-%m-%d'),
                finish_date=datetime.strptime('2018-10-30','%Y-%m-%d'),
                abandoned=False,perler=False,reviewed=False,flagged=False):
    return Game.objects.create(name=name,system=system,played=played,beaten=beaten,
                               location=location,game_format=game_format,notes=notes,
                               purchase_date=purchase_date,finish_date=finish_date,
                               abandoned=abandoned,perler=perler,reviewed=reviewed,flagged=flagged)

def convert_date(date_string):
    return datetime.strptime(date_string,'%Y-%m-%d').date()

#class WishModelTests(TestCase):

class AgingTests(unittest.TestCase):
    @tag('aging')
    def test_aging_zero(self):
        game = create_game(purchase_date=date.today())
        self.assertEqual(game.purchase_date,date.today())
        self.assertEqual(game.aging.days,0)
        self.assertEqual(game.play_aging.days,0)

    @tag('aging')
    def test_aging_over_year(self):
        game = create_game(played=True,beaten=True,purchase_date=datetime.strptime('2016-10-30','%Y-%m-%d'),finish_date=datetime.strptime('2018-10-30','%Y-%m-%d'))
        self.assertEqual(game.purchase_date,datetime.strptime('2016-10-30','%Y-%m-%d'))
        self.assertEqual(game.aging.days,365+365)
        self.assertEqual(game.play_aging.days,0)

    #this is a VALID state due to preorders
    @tag('aging')
    def test_negative_aging(self):
        future_date = date.today() + timedelta(8)
        game = create_game(purchase_date=future_date)
        #self.assertEqual(game.purchase_date,date.today())
        self.assertEqual(game.aging.days,-8)
        self.assertEqual(game.play_aging.days,-8)

    @tag('aging')
    def test_aging_beaten(self):
        game = create_game(purchase_date=date.today()-timedelta(1),beaten=True,finish_date=date.today(),played=True)
        self.assertGreater(game.aging.days,0)
        self.assertEqual(game.play_aging.days,0)
        game = create_game(beaten=True,played=True,purchase_date=date.today(),finish_date=date.today())
        self.assertEqual(game.aging.days,0)
        self.assertEqual(game.play_aging.days,0)

    @tag('aging')
    def test_aging_played(self):
        game = create_game(played=True,purchase_date=date.today()-timedelta(1))
        self.assertEqual(game.aging.days,1)
        self.assertEqual(game.play_aging.days,0)

    @tag('aging')
    def test_aging_abandoned(self):
        game = create_game(purchase_date=date.today()-timedelta(4),abandoned=True,finish_date=date.today(),played=True)
        self.assertEqual(game.aging.days,4)
        self.assertEqual(game.play_aging.days,0)

    @tag('aging')
    def test_aging_not_played(self):
        game = create_game(purchase_date=date.today()-timedelta(5))
        self.assertEqual(game.aging.days,5)
        self.assertEqual(game.play_aging.days,5)

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

class ListDetailRedirectTests(TestCase):
    #client_class = PersistentSessionClient
    def test_known_bad(self):
        game = create_game("Test","3DS",False,False,"3DS","P")
        game2 = create_game("Test 2","GBA",False,False,"3DS","P")
        request = self.client.get(reverse('gameslist:list'),follow=True)
        request = self.client.get(reverse('gameslist:detail',args=(game.id,)),follow=True)
        request = self.client.get(reverse('gameslist:list'),follow=True,HTTP_REFERER="http://127.0.0.1:8000/3/")
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>','<Game: Test 2 - GBA>'])
        self.assertEqual(request.status_code,200)
        
    def test_list(self):
        game = create_game("Test","3DS",False,False,"3DS","P")
        game2 = create_game("Test 2","GBA",False,False,"3DS","P")
        request = self.client.get(reverse('gameslist:list'),{'system':'3DS'},follow=True)
        session = self.client.session
        self.assertEqual(session['query_string'],'system=3DS')
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])

    def test_list_detail(self):
        game = create_game("Test","3DS",False,False,"3DS","P")
        game2 = create_game("Test 2","GBA",False,False,"3DS","P")
        request = self.client.get(reverse('gameslist:list'),{'system':'3DS'},follow=True)
        session = self.client.session
        self.assertEqual(session['query_string'],'system=3DS')
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])
        request = self.client.get(reverse('gameslist:detail',args=(game.id,)),follow=True)  
        self.assertEqual(session['query_string'],'system=3DS')

    def test_list_detail_list(self):
        game = create_game("Test","3DS",False,False,"3DS","P")
        game2 = create_game("Test 2","GBA",False,False,"3DS","P")
        request = self.client.get(reverse('gameslist:list'),{'system':'3DS'},follow=True)
        session = self.client.session
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])

        self.assertEqual(session['query_string'],'system=3DS')
        request = self.client.get(reverse('gameslist:detail',args=(game.id,)),follow=True)
        self.assertEqual(session['query_string'],'system=3DS')
        request = self.client.get(reverse('gameslist:list'),HTTP_REFERER="http://127.0.0.1:8000/3/",follow=True)
        #self.assertQuerysetEqual(request.context['response'].object_list,['<Game: Test - 3DS>'])
        response = request.context['response']
        self.assertQuerysetEqual(response.object_list, ['<Game: Test - 3DS>'])
        self.assertEqual(session['query_string'],'system=3DS')
        self.assertEqual(request.status_code, 200)


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

class ListURLHelperTest(TestCase):

    def test_check_url_args_for_only_token(self):
        self.assertEqual(check_url_args_for_only_token(" "),True)
        self.assertEqual(check_url_args_for_only_token("/"),True)
        self.assertEqual(check_url_args_for_only_token("?"),True)
        self.assertEqual(check_url_args_for_only_token("csrfmiddlewaretoken=xxxyyy22233345455asdfasdf"),True)
        self.assertEqual(check_url_args_for_only_token("csrfmiddlewaretoken=xxxyyy22233345455asdfasdf&page=1"),False)



class HLTBTest(TestCase):
    @tag('hltb')
    def test_example_hltb(self):
        hltb = ExampleHowLongToBeat("Sunset Overdrive")
        self.assertEqual(hltb.game,"Sunset Overdrive")
        self.assertEqual(hltb.fulltime,10.5)

    @tag('htlb')
    def test_known_good_hltb(self):
        hltb = HowLongToBeat("Human Resource Machine")
        self.assertEqual(hltb.game,"Human Resource Machine")
        self.assertEqual(hltb.fulltime,4.5)

    @tag('htlb')
    def test_known_bad_hltb(self):
        hltb = HowLongToBeat("Legion Saga")
        self.assertEqual(hltb.game,"Legion Saga")
        self.assertEqual(hltb.fulltime,-1)

    @tag('htlb')
    def test_alternate_names_hltb(self):
        hltb = HowLongToBeat("Antihero")
        self.assertEqual(str(hltb),"Antihero - Not Found")
        self.assertEqual(hltb.fulltime,-1)

        hltb = HowLongToBeat("Antihero (2017)")
        self.assertEqual(hltb.game,"Antihero (2017)")
        self.assertEqual(hltb.fulltime,6.0)

    @tag('htlb')
    def test_full_time_on_create(self):
        game = create_game("Sunset Overdrive")
        self.assertEqual(game.full_time_to_beat,10.5)

@tag('date_validation')
class GameModelTests(TestCase):
    @tag('date_validation')
    def test_future_purchase_date(self):
        form = GameForm({
            'name': "Test Future Purchase",
            'purchase_date': '2019-01-01',
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM'
        })
        self.assertTrue(convert_date(form.data['purchase_date']) > date.today())
        self.assertRaises(ValidationError,form.full_clean())

    @tag('date_validation')
    def test_past_purchase_date(self):
        form = GameForm({
            'name': "Test Past Purchase",
            'purchase_date': '2018-01-01',
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM'
        })
        self.assertTrue(form.is_valid())

    @tag('date_validation')
    def test_future_finish_date(self):
        form = GameForm({
            'name': "Test Future Finish",
            'finish_date': '2019-01-01',
            'purchase_date': '2018-01-01',
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM'
        })
        self.assertTrue(convert_date(form.data['finish_date']) > date.today())
        print form.data.keys()

        self.assertFalse(form.data['beaten'])
        self.assertRaises(ValidationError,form.full_clean())

    @tag('date_validation')
    def test_past_finish_date(self):
        form = GameForm({
            'name': "Test Past Finish",
            'finish_date': '2018-01-01',
            'purchase_date': '2018-01-01',
            'system': 'STM',
            'game_format': 'D',
            'location': 'STM'
        })
        print vars(form)
        print(form.errors.as_json())
        self.assertFalse(form.data['beaten'])
        self.assertTrue(form.is_valid())

    ##need to validate finish is after purchase?

    # def test_valid_data(self):
    #     form = CommentForm({
    #         'name': "Turanga Leela",
    #         'email': "leela@example.com",
    #         'body': "Hi there",
    #     }, entry=self.entry)
    #     self.assertTrue(form.is_valid())
    #     comment = form.save()
    #     self.assertEqual(comment.name, "Turanga Leela")
    #     self.assertEqual(comment.email, "leela@example.com")
    #     self.assertEqual(comment.body, "Hi there")
    #     self.assertEqual(comment.entry, self.entry)


    # def test_blank_data(self):
    #     form = CommentForm({}, entry=self.entry)
    #     self.assertFalse(form.is_valid())
    #     self.assertEqual(form.errors, {
    #         'name': ['required'],
    #         'email': ['required'],
    #         'body': ['required'],
    #     })

#    def test_list_of_dates(self):
#        print [x for x in range(datetime.now().year-9,datetime.now().year+1)]
#        self.assertEqual(0,1)

        #NEED DIFFERENT RESULTS FOR DIFFERENT STATE

#https://github.com/django/django/blob/master/tests/modeladmin/tests.py