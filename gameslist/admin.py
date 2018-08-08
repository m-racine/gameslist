# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import Game, Owned
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


class OwnedAdmin(admin.ModelAdmin):
    list_display = ('name','system','location','game_format','series','notes','purchase_date','finish_date',
                    'played','beaten','abandoned','perler','reviewed','pursued','substantial_progress','current_time',
                    'times_recommended')
    exclude = ('release_date','developer','publisher','streamable','recordable','aging',
              'play_aging', 'full_time_to_beat','number_of_eps','aging_effect','aging_non_ep',
              'priority','number_of_players','metacritic','user_score','time_to_beat')
    list_filter = ['system','location','series','developer','publisher','played','beaten']
    search_fields = ['name']

admin.site.register(Owned, OwnedAdmin)
