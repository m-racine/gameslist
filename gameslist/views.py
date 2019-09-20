# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date, datetime
import logging
import re
import traceback
#import urlparse
#import urllib
import sys
#from django.template import RequestContext
from django.shortcuts import render, get_object_or_404, reverse
#, redirect, render_to_response
from django.http import HttpResponseRedirect
#HttpResponse, Http404,
from django.views import generic
from django.utils import timezone
from django import forms
from django.forms.utils import ErrorList
#from django.views.generic.edit import CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Game, Wish, Note, SYSTEMS, GameInstance, GameToInstance, AlternateName, TopPriority
from .models import convert_date_fields
from .models import GAME, GAME_INSTANCE, NOTE, ALTERNATE_NAME, WISH, SERIES
from .models import map_single_game_instance, flattenKEY

from .forms import GameInstanceForm, PlayBeatAbandonForm, AlternateNameForm, NoteForm
from .filters import GameInstanceFilter, GameFilter

LOGGER = logging.getLogger('MYAPP')
YOUR_PAGE_SIZE = 10
#https://stackoverflow.com/questions/21153852/plotting-graphs-in-numpy-scipy


class IndexView(generic.ListView):
    template_name = 'gameslist/index.html'
    context_object_name = 'new_games_list'

    def get_queryset(self):
        return Game.objects.filter(
            purchase_date__lte=timezone.now()
        ).order_by('-purchase_date')[:5]

def top_priority_list(request):
    #model = Game
    paginate_by = 10
    game_list = TopPriority.objects.all()
    page = request.GET.get('page')
    paginator = Paginator(game_list, paginate_by)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    request.session['query_string'] = request.GET.urlencode()
    return render(
        request,
        'gameslist/top_priority.html',
        {'response': response}
    )

def filtered_list(request, **kwargs):
    #model = GameInstance
    #paginate_by = YOUR_PAGE_SIZE
    game_list = GameInstance.objects.all().order_by('name')
    if request.META.get('HTTP_REFERER'):
        match = re.search(r'([\d]+)/detail/$', request.META.get('HTTP_REFERER'))
        if match:
            if check_url_args_for_only_token(request.META.get('QUERY_STRING')):
                if check_url_match(reverse('gameslist:detail',
                                           args=(match.group(1), )),
                                   request.META.get('HTTP_REFERER')):
                    if 'query_string' in request.session:
                        if request.session['query_string'].strip():
                            return HttpResponseRedirect(reverse('gameslist:instance_list') +
                                                        "?%s" % (request.session['query_string']))
                        return HttpResponseRedirect(reverse('gameslist:instance_list')+"?page=1")
                    return HttpResponseRedirect(reverse('gameslist:instance_list')+"?page=1")
                else:
                    LOGGER.debug(match.group(1))
            else:
                LOGGER.debug(request.META.get('QUERY_STRING'))
                LOGGER.debug("Query String has search data.")
        else:
            LOGGER.debug("NO INITIAL MATCH")
    else:
        LOGGER.debug("NO REFERER")
    page = request.GET.get('page')
    game_filter = GameInstanceFilter(request.GET, queryset=game_list)

    filtered_qs = game_filter.qs
    paginator = Paginator(filtered_qs, YOUR_PAGE_SIZE)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    request.session['query_string'] = request.GET.urlencode()
    return render(
        request,
        'gameslist/list.html',
        {'response': response, 'filter':game_filter}
    )

def beaten_in_year_list(request, _year=int(date.today().year)):
    #model = GameInstance
    paginate_by = 100
    game_list = GameInstance.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameInstanceFilter({'beaten':True,
                                      'finish_date__year__gte':_year},
                                     queryset=game_list)

    filtered_qs = game_filter.qs
    paginator = Paginator(filtered_qs, paginate_by)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    return render(
        request,
        'gameslist/beaten.html',
        {'response': response, 'filter':game_filter}
    )

def missing_hltb_list(request):
    #model = GameInstance
    paginate_by = 100
    game_list = GameInstance.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameInstanceFilter({'full_time_to_beat':-1.0}, queryset=game_list)

    filtered_qs = game_filter.qs
    paginator = Paginator(filtered_qs, paginate_by)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    return render(
        request,
        'gameslist/missinghltb.html',
        {'response': response, 'filter':game_filter}
    )

def hltb_list(request):
    #model = GameInstance
    paginate_by = 100
    game_list = GameInstance.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameInstanceFilter({'full_time_to_beat__lte':5.0,
                                      'full_time_to_beat__gte':0.1,
                                      'beaten':False}, queryset=game_list)

    filtered_qs = game_filter.qs
    paginator = Paginator(filtered_qs, paginate_by)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    return render(
        request,
        'gameslist/missinghltb.html',
        {'response': response, 'filter':game_filter}
    )

def check_url_match(url, referer):
    for host in ['http://gameslist.griffonflightproductions.com', 'http://127.0.0.1:8000']:
        if re.match("{0}{1}".format(host, url), referer):
            return True
    return False

def check_url_args_for_only_token(url):
    if url:
        temp = url.split("&")
        temp_2 = []
        for tem in temp:
            if tem.split("="):
                temp_2.append(tem.split("="))
            else:
                return True
        dict_temp = {}
        for tem in temp_2:
            if len(tem) < 2:
                return True
            dict_temp[tem[0]] = tem[1]
        return dict_temp.keys() == ['csrfmiddlewaretoken']
    return True


def move_to_detail_view(request, primary):
    game = get_object_or_404(GameInstance, pk=primary)
    #print vars(game)
    #print game.note_set.all()
    return render(request, 'gameslist/detail.html', {'game':game})

class DetailView(generic.DetailView):
    model = GameInstance
    template_name = 'gameslist/detail.html'

def prune_null_finish(dict):
    if dict['finish_date_year'] == 0:
        del dict['finish_date_year']
        del dict['finish_date_day']
        del dict['finish_date_month']
    return dict

def add_game_view(request):
    if request.POST:
        form = GameInstanceForm(request.POST)
        if form.is_valid():
            #print prune_null_finish(request.POST.dict())
            dic = convert_date_fields(prune_null_finish(request.POST.dict()))
            if 'csrfmiddlewaretoken' in dic:
                del dic['csrfmiddlewaretoken']
            if 'played' in dic:
                dic['played'] = True
            if 'beaten' in dic:
                dic['beaten'] = True
            if 'abandoned' in dic:
                dic['abandoned'] = True
            game = GameInstance.objects.create_game_instance(**dic)
            #map_single_game_instance(game.id)
            return render(request, 'gameslist/thanks.html', {'game':game})
        else:
            print form.errors.as_json()
    else:
        form = GameInstanceForm(initial={"purchase_date":date.today()})
    return render(request, 'gameslist/game_form.html', {'form':form})

# def add_note_view(request, game_id):
#     print game_id
#     if request.POST:
#         form = NoteForm(request.POST)
#         if form.is_valid():
#             note = form.save()
#             note.parent_entity_id = game_id
#             print note.parent_entity_id
#             note.save()
#             return HttpResponseRedirect(reverse('gameslist:detail', args=(game_id,)))
#     else:
#         form = NoteForm(initial={"parent_game_id":game_id})
#     return render(request, 'gameslist/note_form.html', {'form':form})

def add_name_view(request, game_id):
    if request.POST:
        form = AlternateNameForm(request.POST)
        if form.is_valid():
            name = form.save()
            name.parent_game_id = game_id
            name.save()
            game = get_object_or_404(GameInstance, pk=game_id)
            game.save()
            return HttpResponseRedirect(reverse('gameslist:detail', args=(game_id,)))
    else:
        form = AlternateNameForm(initial={"parent_game_id":game_id})
    return render(request, 'gameslist/alternatename_form.html', {'form':form})

class PlayBeatAbandonGame(generic.UpdateView):
    model = GameInstance
    form_class = PlayBeatAbandonForm
    template_name_suffix = '_update_form'

    #https://gist.github.com/vero4karu/3b62a13bdce7fe4178ac
    def form_valid(self, form):
        if form.cleaned_data['beaten'] or form.cleaned_data['abandoned']:
            if not form.cleaned_data['finish_date']:
                form._errors[forms.forms.NON_FIELD_ERRORS] = ErrorList([
                    u'You need to have a finish date in order to beat or abandon a game.'
                ])
                return self.form_invalid(form)
        self.object.is_submitted = True
        self.object = form.save()
        game = get_object_or_404(Game, pk=self.object.parent_game_id)
        game.save()
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('gameslist:game_detail', args=(self.object.parent_game_id,))


def save_all_game_instances(request):
    game_list = GameInstance.objects.all()
    for game in game_list:
        if game.metacritic < 1 or game.user_score < 1 or game.active == False:
            try:
                LOGGER.info(unicode(game))
                game.save()
            except:
                LOGGER.warning(unicode(game))
                LOGGER.warning(sys.exc_info()[0])
                LOGGER.warning(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
    return HttpResponseRedirect(reverse('gameslist:list'))

def save_all_games(request):
    game_list = Game.objects.all()
    for game in game_list:
        if game.priority == -4:
            try:
                LOGGER.info(unicode(game))
                game.save()
            except:
                LOGGER.warning(unicode(game))
                LOGGER.warning(sys.exc_info()[0])
                LOGGER.warning(sys.exc_info()[1])
                LOGGER.error(traceback.print_tb(sys.exc_info()[2]))
    return HttpResponseRedirect(reverse('gameslist:list'))


def flag_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    #set game.beat to true
    game.flagged = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

def process_notes():
    games = GameInstance.objects.all()
    for game in games:
        #print game
        if game.notes_old:
            Note.objects.create(text=game.notes_old,
                                created_date=datetime.strptime('2019-1-19', '%Y-%m-%d'),
                                modified_date=datetime.strptime('2019-1-19', '%Y-%m-%d'),
                                parent_game_id=game.id)
    return HttpResponseRedirect(reverse('gameslist:list'))

def fix_location():
    games = GameInstance.objects.all()
    for game in games:
        #maybe use a SWTICH instead?
        if game.location in ["BNT", "DIG", "EPI", "GOG",
                             "HUM", "IND", "IIO",
                             "ORN", "STM", "TWH", "UPL"]:
            game.location = "PC"
        if game.location == "NDS":
            game.location = "3DS"
            game.save()
        elif game.location == "GB":
            game.location = "GBC"
            game.save()
        elif game.location == "PSX":
            game.location = "PS2"
            game.save()
        elif game.location == "WII":
            game.location = "WIU"
            game.save()
        elif game.location == "XBX":
            game.location = "360"
            game.save()
    return HttpResponseRedirect(reverse('gameslist:list'))


def rec_from_list(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    game.times_recommended += 1
    game.save()
    if 'query_string' in request.session:
        return HttpResponseRedirect(reverse('gameslist:list') +
                                    "?{0}".format(request.session['query_string']))
    return HttpResponseRedirect(reverse('gameslist:list'))

    #return render(request, 'gameslist/list.html', context=RequestContext(request).flatten())


def pass_from_list(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    game.times_passed_over += 1
    game.save()
    if 'query_string' in request.session:
        return HttpResponseRedirect(reverse('gameslist:list') +
                                    "?{0}".format(request.session['query_string']))
    return HttpResponseRedirect(reverse('gameslist:list'))

def set_active_inactive_view(request, instance_id):
    instance = get_object_or_404(GameInstance, pk=instance_id)
    instance.set_active_inactive()
    return HttpResponseRedirect(reverse('gameslist:game_detail', args=(instance.parent_game_id,)))

def move_from_instance_to_game(request):
    games = GameInstance.objects.all()
    for game in games:
        map_single_game_instance(game.id)
    return
    #return HttpResponseRedirect(reverse('gameslist:top_priority_list'))

class IndexGameView(generic.ListView):
    template_name = 'gameslist/index.html'
    context_object_name = 'new_games_list'

    def get_queryset(self):
        return Game.objects.filter(
            purchase_date__lte=timezone.now()
        ).order_by('-purchase_date')[:5]

def top_priority_game_list(request):
    #model = Game
    paginate_by = 10
    game_list = Game.objects.all().order_by('-priority')
    paginator = Paginator(game_list, paginate_by)
    page = request.GET.get('page')

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    request.session['query_string'] = request.GET.urlencode()
    return render(
        request,
        'gameslist/top_priority.html',
        {'response': response}
    )

def filtered_game_list(request, **kwargs):
    model = Game
    #paginate_by = YOUR_PAGE_SIZE
    game_list = Game.objects.all().order_by('-priority')
    if request.META.get('HTTP_REFERER'):
        LOGGER.debug(request.META.get('HTTP_REFERER'))
        match = re.search(r'([\d]+)/$', request.META.get('HTTP_REFERER'))
        if match:
            if check_url_args_for_only_token(request.META.get('QUERY_STRING')):
                if check_url_match(reverse('gameslist:detail',
                                           args=(match.group(1), )),
                                   request.META.get('HTTP_REFERER')):
                    LOGGER.debug("REDIRECTING")
                    if 'query_string' in request.session:
                        if request.session['query_string'].strip():
                            return HttpResponseRedirect(reverse('gameslist:list') +
                                                        "?%s" % request.session['query_string'])
                        return HttpResponseRedirect(reverse('gameslist:list') + "?page=1")
                    LOGGER.debug(reverse('gameslist:list') + "?page=1")
                    return HttpResponseRedirect(reverse('gameslist:list') + "?page=1")

    page = request.GET.get('page')
    game_filter = GameFilter(request.GET, queryset=game_list)

    filtered_qs = game_filter.qs
    paginator = Paginator(filtered_qs, YOUR_PAGE_SIZE)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    request.session['query_string'] = request.GET.urlencode()
    return render(
        request,
        'gameslist/game_list.html',
        {'response': response, 'filter':game_filter}
    )

def beaten_in_2018_game_list(request, **kwargs):
    model = Game
    paginate_by = 100
    game_list = Game.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameFilter({'beaten':True, 'finish_date__year__gte':2018}, queryset=game_list)

    filtered_qs = game_filter.qs
    paginator = Paginator(filtered_qs, paginate_by)

    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    return render(
        request,
        'gameslist/beaten.html',
        {'response': response, 'filter':game_filter}
    )


def move_to_detail_view_game(request, primary):
    game = get_object_or_404(Game, pk=primary)
    return render(request, 'gameslist/game_detail.html', {'game':game})

class DetailView_Game(generic.DetailView):
    model = Game
    template_name = 'gameslist/detail.html'

def add_note_plus(request, entity_id, entity_type):
    #need to have notes on a whole game or on an instance etc etc
    if request.POST:
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save()
            note.parent_entity = entity_id
            note.parent_entity_type = entity_type
            note.save()
            return HttpResponseRedirect(reverse('gameslist:detail', args=(entity_id,)))
    else:
        form = NoteForm(initial={"parent_entity_id":entity_id})
    return render(request, 'gameslist/note_form.html', {'form':form})

#DO I NEED THIS?
def add_name_plus(request, entity_id, entity_type):
    #need to have notes on a whole game or on an instance etc etc
    if request.POST:
        form = AlternateNameForm(request.POST)
        if form.is_valid():
            name = form.save()
            name.parent_game_id = game_id
            name.save()
            game = get_object_or_404(GameInstance, pk=game_id)
            game.save()
            return HttpResponseRedirect(reverse('gameslist:detail', args=(game_id,)))
    else:
        form = AlternateNameForm(initial={"parent_game_id":game_id})
    return render(request, 'gameslist/alternatename_form.html', {'form':form})


def flag_game_instance(request, game_id):
    game = get_object_or_404(GameInstance, pk=game_id)
    #set game.beat to true
    game.flagged = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))
