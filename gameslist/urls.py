from django.conf.urls import url

from . import views

app_name = "gameslist"

urlpatterns = [
    url(r'^index/', views.IndexView.as_view(), name='index'),
    #url(r'^by_system(?P<system>\D+)$',views.GameSystemListView.as_view(),name='by_system'),
    #url(r'^(?P<system>[A-z]+)$', views.GameListView.as_view(), name='list'),
    url(r'^add/',views.CreateGame.as_view(), name='add'),
    url(r'^(?P<pk>[0-9]+)/$', views.DetailView.as_view(), name='detail'),
    url(r'^(?P<game_id>[0-9]+)/beat_game/$', views.beat_game, name='beat_game'),
    url(r'^(?P<game_id>[0-9]+)/play_game/$', views.play_game, name='play_game'),
    url(r'^(?P<game_id>[0-9]+)/abandon_game/$', views.abandon_game, name='abandon_game'),
    url(r'^(?P<game_id>[0-9]+)/flag_game/$', views.flag_game, name='flag_game'),
    #url(r'^(?P<system>[\w]*)$', views.set_system, name='set_system'),
    #url(r'^set_format/(?P<format>[\w]*)$', views.set_format, name='set_format'),
    url(r'^$', views.GameListView.as_view(), name='list')]