from django.contrib import admin
from .models import *


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['willer', 'station', 'levels', 'updated']

admin.site.register(Willer)
