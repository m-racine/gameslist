# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Game, GameInstance
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
def wipe_finish(GameAdmin, request, queryset):
    queryset.update(finish_date=None)


class GameInstanceAdmin(admin.ModelAdmin):
    list_display = ('name','system','location','game_format','purchase_date','finish_date',
                    'played','beaten','abandoned','perler','reviewed','flagged')
    exclude = ('release_date','aging',
              'play_aging', 'full_time_to_beat','aging_effect',
              'priority','metacritic','user_score','time_to_beat')
    list_filter = ['system','location','played','beaten','game_format','flagged']
    search_fields = ['name']

    actions = [wipe_finish]

class GameAdmin(admin.ModelAdmin):
    list_display = ('name','purchase_date','finish_date',
                    'played','beaten','abandoned','perler','reviewed','flagged')
    exclude = ('release_date','aging',
              'play_aging', 'full_time_to_beat','aging_effect','aging_non_ep',
              'priority','metacritic','user_score','time_to_beat')
    list_filter = ['played','beaten','flagged']
    search_fields = ['name']

    actions = [wipe_finish]


admin.site.register(GameInstance, GameInstanceAdmin)
admin.site.register(Game, GameAdmin)
