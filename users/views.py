from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

def login_user(request):
    return render(request, 'users/login.html')  


@csrf_exempt
def profile(request):
    from home.models import Text
    from .models import UserProfile
    from django.contrib.auth.forms import AuthenticationForm
    from django.contrib.auth import authenticate, login
    from django.shortcuts import redirect
    import json


    if request.method == 'POST':
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            data = json.loads(request.body)

            profile, created = UserProfile.objects.update_or_create(user=request.user, defaults={'profile': data})
            return JsonResponse(profile.profile)


    context = {}

    # Se Ajax request, return JSON
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if request.user.is_authenticated:
            profile = UserProfile.objects.filter(user=request.user).first()
            if profile:
                return JsonResponse(profile.profile)
        return JsonResponse({'esigenze': []})
    
    texts = {t.code: t.get_text for t in Text.objects.all()}
    context['texts'] = texts

    login_form = AuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and 'login' in request.POST:
        if login_form.is_valid():
            username = login_form.cleaned_data.get('username')
            password = login_form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/')
        
    context['login_form'] = login_form

    return render(request, 'users/profile.html', context)


def register(request):
    from .forms import UserEmailCreationForm
    from django.contrib.auth import login, authenticate
    from django.shortcuts import redirect
    from django.urls import reverse

    context = {}

    register_form = UserEmailCreationForm(request.POST or None)
    if request.method == 'POST':
        if register_form.is_valid():
            user = register_form.save()
            login(request, user)
            return redirect(reverse('profile'))

    context['register_form'] = register_form

    return render(request, 'users/register.html', context)