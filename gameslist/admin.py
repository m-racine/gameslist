# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Game
# Register your models here.


# class ChoiceInline(admin.TabularInline):
#     model = Choice
#     extra = 3

# class QuestionAdmin(admin.ModelAdmin):
#     list_display = ('question_text', 'pub_date', 'was_published_recently')
#     fieldsets = [
#                 (None, {'fields': ['question_text']}),
#                 ('Date information', {'fields': ['pub_date'], 'classes': ['collapse']}),
#                 ]
#     inlines = [ChoiceInline]
#     list_filter = ['pub_date']
#     search_fields = ['question_text']

#admin.site.register(Question, QuestionAdmin)


class GameAdmin(admin.ModelAdmin):
    list_display = ('name','system','location','game_format','notes','purchase_date','finish_date',
                    'played','beaten','abandoned','perler','reviewed')
    exclude = ('release_date','developer','publisher','streamable','recordable','aging',
              'play_aging', 'full_time_to_beat','number_of_eps','aging_effect','aging_non_ep',
              'priority','number_of_players','metacritic','user_score','time_to_beat')
    list_filter = ['system','location','played','beaten']
    search_fields = ['name']

admin.site.register(Game, GameAdmin)
