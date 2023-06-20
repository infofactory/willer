from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import translation

from .models import *

@csrf_exempt
def home(request):

    context = {}

    texts = {t.code: t.get_text for t in Text.objects.all()}
    context['texts'] = texts


    if request.method == 'POST':
        context = {}
        email = request.POST.get('email')
        nickname = request.POST.get('nickname')
        willer = Willer.objects.filter(email=email, nickname__iexact=nickname).first()
        if not willer:
            if Willer.objects.filter(email__iexact=email).exists():
                messages.error(request, 'The e-mail has already been used with another nickname.')
                request.session.pop('willer', None)
            elif Willer.objects.filter(nickname__iexact=nickname).exists():
                messages.error(request, 'The nickname has already been used with another email.')
                request.session.pop('willer', None)
            else:
                willer = Willer.objects.create(email=email, nickname=nickname)

        if willer:
            request.session['willer'] = willer
            return redirect('/')
    
    if 'new-area' in request.GET:
        # Nuova area della stessa stazione, mantengo tipo e numero di piani
        old_answer = request.session.pop('answer', None)
        if old_answer:
            answer = Answer.objects.create(willer = old_answer.willer, station=old_answer.station, levels=old_answer.levels, lat=old_answer.lat, lng=old_answer.lng)
            request.session['answer'] = answer

        context['page'] = 4

    elif 'new-auditing' in request.GET:
        request.session.pop('answer', None)
        context['page'] = 1

    elif 'new-user' in request.GET:
        request.session.pop('willer', None)
        request.session.pop('answer', None)

    return render(request, 'home/index.html', context)

@csrf_exempt
def save(request):
    if request.method == 'POST':
        willer = request.session['willer']

        answer = request.session.get('answer') or Answer.objects.create(willer = willer)
        for k,v in request.POST.items():
            setattr(answer, k, v)
            answer.save()
        for k,v in request.FILES.items():
            setattr(answer, k, v)
            answer.save()
        request.session['answer'] = answer
        return HttpResponse('OK')

    return HttpResponse('Solo richieste in POST', status=405)


def best_willers(request):
    from django.db.models import Count

    willers = Willer.objects.annotate(total_answers=Count('answers')).order_by('-total_answers')[:20]
    context = {'willers':willers}
    return render(request, 'home/best.html', context)
