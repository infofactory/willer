from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .models import Stop, Lift
from home.models import Luogo, Area

import math
import requests

PLACE_API_URL = 'https://api.willeasy.app/api/nearbysearch/json'
WILL_KEY = 'AIzaSyDIX902GGnebHfa7QplbMa'

def places(request):

    location_type = request.GET.get('location_type', 'M')



    print(location_type)

    places = []

    if location_type == 'M':
    # Escludo le stazioni che hanno solo scale e quelle che sono senza coordinate
        places = Stop.objects.filter(location_type=Stop.STATION, lat__isnull=False, lon__isnull=False, lifts__type__in = [Lift.LIFT, Lift.STAIRLIFT, Lift.ESCALATOR]).order_by('name').distinct()



    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    if lat and lng:
        lat = float(lat)
        lng = float(lng)



        if location_type == 'R':
            params = {
                'location': f'{lat},{lng}',
                'radius': 1500,
                'type': 'restaurant',
                'key': WILL_KEY
            }

            response = requests.get(PLACE_API_URL, params=params)
            print(response.url)
            data = response.json()
            print(data)

            for result in data:
                place = Luogo()
                place.name = result['name']
                place.lat = result['geometry']['location']['lat']
                place.lon = result['geometry']['location']['lng']
                places.append(place)

        for place in places:
            # Calculate distance from current location
            place.distance = math.sqrt((place.lat - lat)**2 + (place.lon - lng)**2)
        
        places = sorted(places, key=lambda x: x.distance)[:location_type == 'M' and 1 or 20]

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
            domanda_json = {'domanda': domanda.domanda, 'pk':domanda.pk, 'type':domanda.type, 'risposte': []}
            for risposta in domanda.risposte.all():
                domanda_json['risposte'].append({'pk':risposta.pk, 'risposta': risposta.risposta})

            area_json['domande'].append(domanda_json)

        area_questions.append(area_json)
    return JsonResponse(area_questions, safe=False)


@csrf_exempt
def segnalazioni(request):
    from .models import Segnalazione
    if request.method == 'POST':
        lift_id = request.POST.get('lift', None)
        status = request.POST.get('status', None)
        try:
            user = request.user.is_authenticated and request.user or None
            Segnalazione.objects.create(user=user, lift_id=lift_id, working=status)
            return HttpResponse('OK', status=201) # no content
        except:
            raise
            return HttpResponse('Error', status=500)
    # method not allowed
    return HttpResponse('Error', status=405)
