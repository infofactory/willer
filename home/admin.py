from django.contrib import admin
from .models import *


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ['willer', 'station', 'levels', 'updated']

@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    list_display = ['label', 'label_it']

admin.site.register(Willer)

admin.site.register(Area)
admin.site.register(Luogo)

class RispostaInline(admin.TabularInline):
    model = Risposta
    extra = 0

class DomandaAdmin(admin.ModelAdmin):
    list_display = ['domanda', 'area', 'ordine']
    list_filter = ['area']
    inlines = [RispostaInline]
admin.site.register(Domanda, DomandaAdmin)

