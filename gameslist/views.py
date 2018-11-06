# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date
import logging,re
from django.shortcuts import render,get_object_or_404, reverse
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django.views.generic.edit import CreateView

from .models import Game,Wish,GameForm

# Create your views here.
logger = logging.getLogger('MYAPP')
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
        request_system = self.request.GET.get('system')
        #self.request.GET.set('s')
        request_game_format = self.request.GET.get('format')
        if 'HTTP_REFERER' in self.request.environ:
            logger.debug(self.request.environ['HTTP_REFERER'])
            if re.search(r'(?P<pk>[0-9]+)/$',self.request.environ['HTTP_REFERER']):
                logger.debug("MATCH")
            else:
                logger.debug("NOT A MATCH")
        if 'system' in self.request.session:
            system = self.request.session['system']
        else:
            system = False
        if 'format' in self.request.session:
            game_format = self.request.session['format']
        else:
            game_format = False
        if system and game_format:
            return Game.objects.filter(system=system).filter(game_format=game_format).order_by('name')
        elif system:
            return Game.objects.filter(system=system).order_by('name')
        elif game_format:
            return Game.objects.filter(game_format=game_format).order_by('name')
        else:
            return Game.objects.all().order_by('name')

def set_system(request, system):
    request.session['system'] = system
    return HttpResponseRedirect(reverse('gameslist:list'))

def set_format(request, game_format):
    request.session['format'] = game_format
    return HttpResponseRedirect(reverse('gameslist:list'))

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

#def play_game(request, game_id):
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

def flag_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    #set game.beat to true
    game.flagged = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

# def games_by_system(self):
#     system = "3DS"
#     urlparams = '?system=%s' % (system)    
#     return redirect(reverse('gameslist:by_system')+urlparams)



# # Some standard Django stuff
# from django.http import HttpResponse, HttpResponseRedirect, Http404
# from django.template import Context, loader
 
# # list of mobile User Agents
# mobile_uas = [
#     'w3c ','acs-','alav','alca','amoi','audi','avan','benq','bird','blac',
#     'blaz','brew','cell','cldc','cmd-','dang','doco','eric','hipt','inno',
#     'ipaq','java','jigs','kddi','keji','leno','lg-c','lg-d','lg-g','lge-',
#     'maui','maxo','midp','mits','mmef','mobi','mot-','moto','mwbp','nec-',
#     'newt','noki','oper','palm','pana','pant','phil','play','port','prox',
#     'qwap','sage','sams','sany','sch-','sec-','send','seri','sgh-','shar',
#     'sie-','siem','smal','smar','sony','sph-','symb','t-mo','teli','tim-',
#     'tosh','tsm-','upg1','upsi','vk-v','voda','wap-','wapa','wapi','wapp',
#     'wapr','webc','winw','winw','xda','xda-'
#     ]
 
# mobile_ua_hints = [ 'SymbianOS', 'Opera Mini', 'iPhone' ]
 
 
# def mobileBrowser(request):
#     ''' Super simple device detection, returns True for mobile devices '''
 
#     mobile_browser = False
#     ua = request.META['HTTP_USER_AGENT'].lower()[0:4]
 
#     if (ua in mobile_uas):
#         mobile_browser = True
#     else:
#         for hint in mobile_ua_hints:
#             if request.META['HTTP_USER_AGENT'].find(hint) > 0:
#                 mobile_browser = True
 
#     return mobile_browser
 
 
# def index(request):
#     '''Render the index page'''
 
#     if mobileBrowser(request):
#         t = loader.get_template('m_index.html')
#     else:
#         t = loader.get_template('index.html')
 
#     c = Context( { }) # normally your page data would go here
 
#     return HttpResponse(t.render(c))\

#Mobile Views taken from 
#https://mobiforge.com/design-development/build-a-mobile-and-desktop-friendly-application-django-15-minutes