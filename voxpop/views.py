from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse

from .models import Stop, Lift
from home.models import Luogo, Area

import math

def places(request):

    location_type = request.GET.get('location_type', 'M')

    places = []

    if location_type == 'M':
    # Escludo le stazioni che hanno solo scale e quelle che sono senza coordinate
        places = Stop.objects.filter(location_type=Stop.STATION, lat__isnull=False, lon__isnull=False, lifts__type__in = [Lift.LIFT, Lift.STAIRLIFT, Lift.ESCALATOR]).order_by('name').distinct()

    elif location_type == 'R':
        places = Luogo.objects.all()


    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    if lat and lng:
        lat = float(lat)
        lng = float(lng)
        for place in places:
            # Calculate distance from current location
            place.distance = math.sqrt((place.lat - lat)**2 + (place.lon - lng)**2)
        
        places = sorted(places, key=lambda x: x.distance)[:3]

    data = serializers.serialize("json", places)
    return HttpResponse(data, content_type='application/json')

def lifts(request):
    
    data = '[]'
    station_id = request.GET.get('station_id', None)

    stops_dict = {stop.pk: str(stop) for stop in Stop.objects.all()}
    if station_id:
        lifts = Lift.objects.filter(stop_id=station_id).exclude(type=Lift.STAIR).select_related('from_area')
        data = serializers.serialize("json", lifts)
        obj_data = serializers.serialize("python", lifts)
        print(obj_data)

        for lift in obj_data:
            lift['fields']['from_area'] = stops_dict.get(lift['fields']['from_area'])
            lift['fields']['to_area'] = stops_dict.get(lift['fields']['to_area'])

        return JsonResponse(obj_data, safe=False)

    return HttpResponse(data, content_type='application/json')


def areas(request):
    area_questions = []
    areas = Area.objects.all()
    for area in areas:
        area_json = {'nome': area.nome, 'domande': []}

        for domanda in area.domande.all():
            domanda_json = {'domanda': domanda.domanda, 'pk':domanda.pk, 'multi':domanda.multi, 'risposte': []}
            for risposta in domanda.risposte.all():
                domanda_json['risposte'].append({'pk':risposta.pk, 'risposta': risposta.risposta})

            area_json['domande'].append(domanda_json)

        area_questions.append(area_json)
    return JsonResponse(area_questions, safe=False)