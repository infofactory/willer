from django.contrib import admin
from django.forms import CheckboxSelectMultiple

from .models import *

admin.site.register(Willer)

admin.site.register(Categoria)
admin.site.register(Esigenza)
admin.site.register(Luogo)

@admin.register(Text)
class TextAdmin(admin.ModelAdmin):
    list_display = ['code', 'get_text_short']

@admin.register(Area)
class AreaAdmin(admin.ModelAdmin):
    list_display = ['nome', 'ordine', 'categoria']


class RispostaInline(admin.TabularInline):
    model = Risposta
    extra = 0

class DomandaAdmin(admin.ModelAdmin):
    list_display = ['domanda', 'area', 'ordine']
    list_filter = ['area']
    
    formfield_overrides = {
        models.ManyToManyField: {'widget': CheckboxSelectMultiple},
    }

    inlines = [RispostaInline]
admin.site.register(Domanda, DomandaAdmin)


class RilevazioneAdmin(admin.ModelAdmin):
    list_display = ['luogo', 'domanda', 'risposta_text', 'user', 'data']
admin.site.register(Rilevazione, RilevazioneAdmin)

