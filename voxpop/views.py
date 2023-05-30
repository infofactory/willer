from django.shortcuts import render
from django.core import serializers
from django.http import JsonResponse, HttpResponse

from .models import Stop, Lift

import math

def stations(request):
    # Escludo le stazioni che hanno solo scale e quelle che sono senza coordinate
    stations = Stop.objects.filter(location_type=Stop.STATION, lat__isnull=False, lon__isnull=False, lifts__type__in = [Lift.LIFT, Lift.STAIRLIFT, Lift.ESCALATOR]).order_by('name').distinct()

    lat = request.GET.get('lat', None)
    lng = request.GET.get('lng', None)
    if lat and lng:
        lat = float(lat)
        lng = float(lng)
        for station in stations:
            # Calculate distance from current location
            station.distance = math.sqrt((station.lat - lat)**2 + (station.lon - lng)**2)
        
        stations = sorted(stations, key=lambda x: x.distance)[:3]

    data = serializers.serialize("json", stations)
    return HttpResponse(data, content_type='application/json')

def lifts(request):
    
    data = '[]'
    station_id = request.GET.get('station_id', None)
    if station_id:
        lifts = Lift.objects.filter(stop_id=station_id).exclude(type=Lift.STAIR)
        data = serializers.serialize("json", lifts)

    return HttpResponse(data, content_type='application/json')