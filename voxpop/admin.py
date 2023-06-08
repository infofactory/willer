from django.contrib import admin

from .models import *


class StopAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'get_location_type_display']
admin.site.register(Stop, StopAdmin)

class CityAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(City, CityAdmin)

admin.site.register(Lift)

class SegnalazioneAdmin(admin.ModelAdmin):
    list_display = ['lift', 'working', 'user', 'created']
admin.site.register(Segnalazione, SegnalazioneAdmin)
