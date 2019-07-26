from django.conf.urls import url

from . import views

app_name = "gameslist"

urlpatterns = [
    url(r'^index/', views.IndexView.as_view(), name='index'),
    #url(r'^add/',views.CreateGame.as_view(), name='add'),
    url(r'^add/', views.add_game_view, name='add'),
    url(r'^(?P<primary>[0-9]+)/detail/$', views.move_to_detail_view, name='detail'),
    url(r'^(?P<primary>[0-9]+)/$', views.move_to_detail_view_game, name='game_detail'),
    url(r'^(?P<pk>[0-9]+)/play_game/$', views.PlayBeatAbandonGame.as_view(), name='play_game'),
    url(r'^(?P<game_id>[0-9]+)/flag_game/$', views.flag_game, name='flag_game'),
    url(r'^(?P<instance_id>[0-9]+)/activate/$', views.set_active_inactive_view, name='activate'),
    url(r'^(?P<game_id>[0-9]+)/recommend/$', views.rec_from_list, name='recommend'),
    url(r'^(?P<game_id>[0-9]+)/pass_over/$', views.pass_from_list, name='pass_over'),
    url(r'^(?P<game_id>[0-9]+)/add_note/$', views.add_note_view, name='add_note'),
    url(r'^(?P<game_id>[0-9]+)/add_name/$', views.add_name_view, name='add_name'),
    #url(r'^test-delete/$', views.test_delete, name='test_delete'),
    #url(r'^test-session/$', views.test_session, name='test_session'),
    #url(r'^stop-tracking/$', views.stop_tracking, name='stop_tracking'),
    url(r'^save-all/$', views.save_all_games, name='save_all'),
    url(r'^beaten/?P<_year>[0-9]+$', views.beaten_in_year_list, name='beaten'),
    url(r'^$', views.top_priority_list, name='top_priority_list'),
    #url(r'^hltb/$', views.missing_hltb_list, name='hltb'),
    url(r'^process_games/$', views.move_from_instance_to_game, name='process_games'),
    #url(r'^locate/$', views.fix_location, name='locate'),
    #url(r'^notes/$', views.process_notes, name='notes'),
    url(r'^full$', views.filtered_game_list, name='list', kwargs=dict({'page':''})),
    url(r'^full$', views.filtered_game_list, name='list'),
    url(r'^instance$', views.filtered_list, name='instance_list', kwargs=dict({'page':'', 'system':'', 'game_format':''})),
    url(r'^instance$', views.filtered_list, name='instance_list')]


###notes: need to change detail page to show list of notes associated
###add note
###delete note
###modify note
###
###alternate names:
###follow same format, but we don't need to convert initial name maybe?
###metacritc needs to be pulled into play
###
###MOAR SORTING AND SEARCHING
###by LENGTH
###BY PRIORITY
###BY started?
