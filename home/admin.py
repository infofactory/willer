from django.contrib import admin
from .models import *


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['willer', 'station', 'levels', 'updated']

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ['label', 'label_it']

admin.site.register(Willer)
