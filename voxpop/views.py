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

    places = []

    if location_type == 'M':
    # Escludo le stazioni che hanno solo scale e quelle che sono senza coordinate
        places = Stop.objects.filter(location_type=Stop.STATION, lat__isnull=False, lon__isnull=False, lifts__type__in = [Lift.LIFT, Lift.STAIRLIFT, Lift.ESCALATOR]).order_by('name').distinct()



    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    query = request.GET.get('query', None)
    if lat and lng:
        lat = float(lat)
        lng = float(lng)

        params = {
                'location': f'{lat},{lng}',
                'radius': 1500,
                'key': WILL_KEY
            }
        if query:
            params['keyword'] = query
        data = []

        if location_type == 'R':
      
            params['type'] = 'restaurant'
            response = requests.get(PLACE_API_URL, params=params)
            data = response.json()

            # Controllo duplicati basandomi sul place_id
            place_ids = [result['place_id'] for result in data]

            params['type'] = 'bar'
            response = requests.get(PLACE_API_URL, params=params)
            bars = response.json()
            data.extend([bar for bar in bars if bar['place_id'] not in place_ids])

        if location_type == 'H':
            params['type'] = 'lodging'
            params['radius'] = 5000
            response = requests.get(PLACE_API_URL, params=params)
            data = response.json()

        for result in data:
            place, created = Luogo.objects.get_or_create(place_id=result['place_id'], defaults={'name': result['name']}, lat=result['geometry']['location']['lat'], lon=result['geometry']['location']['lng'], address=result['vicinity'])
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

        for lift in obj_data:
            lift['fields']['from_area'] = stops_dict.get(lift['fields']['from_area'])
            lift['fields']['to_area'] = stops_dict.get(lift['fields']['to_area'])

        return JsonResponse(obj_data, safe=False)

    return HttpResponse(data, content_type='application/json')



def esigenze(request):
    from home.models import Esigenza
    data = serializers.serialize("json", Esigenza.objects.all())
    return HttpResponse(data, content_type='application/json')




def areas(request):
    from django.db.models import Q

    category = request.GET.get('category', 'R')
    esigenze = request.GET.get('esigenze', '')
    if esigenze:
        esigenze = esigenze.split(',')
        esigenze = [int(esigenza) for esigenza in esigenze]

    area_questions = []
    areas = Area.objects.filter(categoria__code = category)
    for area in areas:
        area_json = {'nome': area.nome, 'domande': []}

        for domanda in area.domande.filter(Q(esigenza__in=esigenze) | Q(esigenza__isnull=True)).distinct():
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
            return HttpResponse('Error', status=500)
    # method not allowed
    return HttpResponse('Error', status=405)


@csrf_exempt
def rilevazioni(request):
    from home.models import Rilevazione, Domanda
    from django.core.files.base import ContentFile
    import json
    import base64


    if request.method == 'POST':
        data = json.loads(request.body)

        client_ip = get_client_ip(request)
        try:
            user = request.user.is_authenticated and request.user or None
            luogo = data['luogo']
            for domanda_id, risposta in data['rilevazioni'].items():
                domanda = Domanda.objects.get(pk=domanda_id)
                if risposta:
                    # caso particolare per le domande di tipo checkbox multiple
                    if domanda.type == 'checkbox':
                        for r in risposta:
                            Rilevazione.objects.create(user=user, luogo_id=luogo, domanda=domanda, ip_address=client_ip, risposta_id=r)
                        continue

                    # foto in base64
                    if domanda.type == 'image':
                        for r in risposta:
                            image_b64 = r['image']
                            imgstr = image_b64.split(';base64,')[-1]
                            data = ContentFile(base64.b64decode(imgstr), name=r['name'])
                            Rilevazione.objects.create(user=user, luogo_id=luogo, domanda=domanda, ip_address=client_ip, image=data)
                        continue

                    # caso generale
                    r = Rilevazione.objects.create(user=user, luogo_id=luogo, domanda=domanda, ip_address=client_ip)
                    if r.domanda.type == 'radio':
                        r.risposta_id = risposta
                    else:
                        r.value = risposta
                    r.save()


            return HttpResponse('OK', status=201) # no content
        except:
            raise
            return HttpResponse('Error', status=500)
    # method not allowed
    return HttpResponse('Error', status=405)



# https://stackoverflow.com/questions/4581789/how-do-i-get-user-ip-address-in-django
def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip