# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import date,datetime
import logging,re,traceback
import urlparse
import urllib
import sys
from django.shortcuts import render,get_object_or_404, reverse, redirect
from django.http import HttpResponse, Http404, HttpResponseRedirect
from django.views import generic
from django.utils import timezone
from django import forms
from django.forms.utils import ErrorList
from django.views.generic.edit import CreateView
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Game,Wish,Note, SYSTEMS
from .forms import GameForm,PlayBeatAbandonForm,AlternateNameForm,NoteForm
from .filters import GameFilter

# Create your views here. 
logger = logging.getLogger('MYAPP')
#YOUR_PAGE_SIZE = len(SYSTEMS)
YOUR_PAGE_SIZE = 10
#https://stackoverflow.com/questions/21153852/plotting-graphs-in-numpy-scipy

class IndexView(generic.ListView):
    template_name = 'gameslist/index.html'
    context_object_name = 'new_games_list'

    def get_queryset(self):
        return Game.objects.filter(
            purchase_date__lte=timezone.now()
        ).order_by('-purchase_date')[:5]
    
def top_priority_list(request,**kwags):
    model = Game
    paginate_by = len(SYSTEMS)

    # wanted_items = set()
    # for item in model1.objects.all():
    #     if check_want_item(item):
    #         wanted_items.add(item.pk)

    # return model1.objects.filter(pk__in = wanted_items)
    top_dict = {}
    game_list = Game.objects.all().order_by('-priority')
    for item in game_list:
        if item.location in top_dict:
            pass
        else:
            top_dict[item.location] = item.id
        if len(top_dict.keys()) == paginate_by:
            break
    page = request.GET.get('page')
    filtered_set = set(top_dict.values())
    #print filtered_set
    filtered_qs = Game.objects.filter(pk__in = filtered_set).order_by('-priority')
    paginator = Paginator(filtered_qs, paginate_by)

    
    try:
        response = paginator.page(page)
    except PageNotAnInteger:
        response = paginator.page(1)
    except EmptyPage:
        response = paginator.page(paginator.num_pages)
    except:
        response = paginator.page(1)
    request.session['query_string'] =request.GET.urlencode()
    return render(
         request, 
         'gameslist/top_priority.html', 
         {'response': response}
    )

def filtered_list(request,**kwargs):
    model = Game
    paginate_by = YOUR_PAGE_SIZE
    #game_list = Game.objects.all().order_by('-purchase_date')
    #game_list = Game.objects.all().order_by('-priority')
    game_list = Game.objects.all().order_by('name')
    #logger.debug(kwargs)
    if request.META.get('HTTP_REFERER'):
        logger.debug(request.META.get('HTTP_REFERER'))
        match = re.search(r'([\d]+)/$',request.META.get('HTTP_REFERER'))
        if match:
            if check_url_args_for_only_token(request.META.get('QUERY_STRING')):
                if check_url_match(reverse('gameslist:detail', args=(match.group(1),)),request.META.get('HTTP_REFERER')):
                    logger.debug("REDIRECTING")
                    if 'query_string' in request.session:
                        if request.session['query_string'].strip():
                            return HttpResponseRedirect(reverse('gameslist:list')+"?{0}".format(request.session['query_string']))
                        return HttpResponseRedirect(reverse('gameslist:list')+"?page=1")
                    logger.debug(reverse('gameslist:list')+"?page=1")
                    return HttpResponseRedirect(reverse('gameslist:list')+"?page=1")
                    
            #else:
            #    logger.debug(request.META.get('QUERY_STRING'))
            #    logger.debug("Query String has search data.")
        #else:
        #    logger.debug("NO INITIAL MATCH")
    #else:
    #    logger.debug("NO REFERER")
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
    request.session['query_string'] =request.GET.urlencode()
    return render(
         request, 
         'gameslist/list.html', 
         {'response': response,'filter':game_filter}
    )

def beaten_in_2018_list(request,**kwargs):
    model = Game
    paginate_by = 100
    game_list = Game.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameFilter({'beaten':True,'finish_date__year__gte':2018}, queryset=game_list)
    
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
         {'response': response,'filter':game_filter}
    )

def missing_hltb_list(request,**kwargs):
    model = Game
    paginate_by = 100
    game_list = Game.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameFilter({'full_time_to_beat':-1.0}, queryset=game_list)
    
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
         {'response': response,'filter':game_filter}
    )

def hltb_list(request,**kwargs):
    model = Game
    paginate_by = 100
    game_list = Game.objects.all().order_by('system')

    page = request.GET.get('page')
    game_filter = GameFilter({'full_time_to_beat__lte':5.0,'full_time_to_beat__gte':0.1,'beaten':False}, queryset=game_list)
    
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
         {'response': response,'filter':game_filter}
    )

def check_url_match(url,referer):
    for host in ['http://gameslist.griffonflightproductions.com','http://127.0.0.1:8000']:
        logger.debug("{0}{1}".format(host,url))
        logger.debug(referer)
        if re.match("{0}{1}".format(host,url),referer):
            return True
    return False

def check_url_args_for_only_token(url):
    if url:
        temp = url.split("&")
        temp_2 = []
        for x in temp:
            if x.split("="):
                temp_2.append(x.split("="))
            else:
                return True
        dict_temp = {}
        for x in temp_2:
            if len(x) < 2:
                return True
            dict_temp[x[0]] = x[1]
        if dict_temp.keys() == ['csrfmiddlewaretoken']:
            return True
        else:
            return False
    return True


def move_to_detail_view(request, pk):
    game = get_object_or_404(Game, pk=pk)
    #print vars(game)
    #print game.note_set.all()
    return render(request, 'gameslist/detail.html', {'game':game})

class DetailView(generic.DetailView):
    model = Game
    template_name = 'gameslist/detail.html'

def add_game_view(request):
    if request.POST:
        form = GameForm(request.POST)
        if form.is_valid():
            game = form.save()
            game.save()
            return render(request,'gameslist/thanks.html', {'game':game})
    else:
        form = GameForm(initial={"purchase_date":date.today()})
    return render(request,'gameslist/game_form.html', {'form':form})

def add_note_view(request,game_id):
    if request.POST:
        form = NoteForm(request.POST)
        if form.is_valid():
            note = form.save()
            note.parent_game_id = game_id
            note.save()
            return HttpResponseRedirect(reverse('gameslist:detail', args=(game_id,)))
    else:
        form = NoteForm(initial={"parent_game_id":game_id})
    return render(request,'gameslist/note_form.html', {'form':form})

def add_name_view(request,game_id):
    if request.POST:
        form = AlternateNameForm(request.POST)
        if form.is_valid():
            name = form.save()
            name.parent_game_id = game_id
            name.save()
            game = get_object_or_404(Game, pk=game_id)
            game.save()
            return HttpResponseRedirect(reverse('gameslist:detail', args=(game_id,)))
    else:
        form = AlternateNameForm(initial={"parent_game_id":game_id})
    return render(request,'gameslist/alternatename_form.html', {'form':form})

class PlayBeatAbandonGame(generic.UpdateView):
    model = Game
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
        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse('gameslist:detail', args=(self.object.id,))

def save_all_games(request):
    game_list = Game.objects.all()
    for game in game_list:
        if game.metacritic < 1 or game.user_score < 1 or game.full_time_to_beat < 1:
            try:
                logger.info(unicode(game))
                #game.clean()
                game.save()
            except:
                logger.warning(unicode(game))
                logger.warning(sys.exc_info()[0])
                logger.warning(sys.exc_info()[1])
                logger.error(traceback.print_tb(sys.exc_info()[2]))
    return HttpResponseRedirect(reverse('gameslist:list'))
# def beat_game(request, game_id):
#     game = get_object_or_404(Game, pk=game_id)
#     #set game.beat to true
#     game.beaten = True
#     game.save()
#     return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

# #def play_game(request, game_id):
# def play_game(request, game_id):
#     game = get_object_or_404(Game, pk=game_id)
#     #set game.beat to true
#     game.played = True
#     game.save()
#     return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

# def abandon_game(request, game_id):
#     game = get_object_or_404(Game, pk=game_id)
#     #set game.beat to true
#     game.abandoned = True
#     game.save()
#     return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

def flag_game(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    #set game.beat to true
    game.flagged = True
    game.save()
    return HttpResponseRedirect(reverse('gameslist:detail', args=(game.id,)))

#...
def stop_tracking(request):
#...
    return HttpResponse("Stop?")

def test_session(request):
    request.session.set_test_cookie()
    return HttpResponse("Testing session cookie")


def test_delete(request):
    if request.session.test_cookie_worked():
        request.session.delete_test_cookie()
        response = HttpResponse("Cookie test passed")
    else:
        response = HttpResponse("Cookie test failed")
    return response

def process_notes(request):
    games = Game.objects.all()
    for game in games:
        #print game
        if game.notes_old:
            Note.objects.create(text=game.notes_old,created_date=datetime.strptime('2019-1-19', '%Y-%m-%d'),
                                modified_date=datetime.strptime('2019-1-19', '%Y-%m-%d'),parent_game_id=game.id)
    return HttpResponseRedirect(reverse('gameslist:list'))

def fix_location(request):
    games = Game.objects.all()
    for game in games:
        #print game
        if game.location in ["BNT","DIG","EPI","GOG","HUM","IND","IIO","ORN","STM","TWH","UPL"]:
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
    logger.DEBUG(request)
    game.times_recommended += 1
    game.save()
    return HttpResponseRedirect(reverse('gameslist:list'))

def pass_from_list(request, game_id):
    game = get_object_or_404(Game, pk=game_id)
    game.times_passed_over += 1
    game.save()
    return HttpResponseRedirect(reverse('gameslist:list'))

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