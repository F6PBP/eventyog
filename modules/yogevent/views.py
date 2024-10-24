from django.shortcuts import get_object_or_404, render, redirect, reverse
from modules.yogevent.forms import EventForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from modules.main.models import *
from eventyog.decorators import check_user_profile
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.db.models import Q

@check_user_profile(is_redirect=True)
def show_main(request: HttpRequest) -> HttpResponse:
    user_profiles = UserProfile.objects.all()
    events = Event.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        events = events.filter(Q(title__icontains=query) | Q(description__icontains=query))

    if category:
        events = events.filter(category=category)

    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.user_profile.role == 'AD',
        'users': user_profiles,
        'events': events,
    }
    return render(request, 'yogevent.html', context)

def show_event_xml(request):    
    user_profile = getattr(request.user, 'userprofile', None)
    if user_profile:
        events = Event.objects.filter(userprofile=user_profile)
    else:
        events = Event.objects.all()

    return HttpResponse(serializers.serialize("xml", events), content_type="application/json") 

def show_event_json(request):
    user_profile = getattr(request.user, 'userprofile', None)
    if user_profile:
        events = Event.objects.filter(userprofile=user_profile)
    else:
        events = Event.objects.all()
    return HttpResponse(serializers.serialize("json", events), content_type="application/json") 

def show_xml_event_by_id(request, id):
    data = Event.objects.filter(pk=id)  # Cari event berdasarkan primary key
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_event_by_id(request, id):
    data = Event.objects.filter(pk=id)  # Cari event berdasarkan primary key
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

@check_user_profile(is_redirect=True)
@csrf_exempt
@require_POST
def create_event_entry_ajax(request):
    categories = [
        ('OL', 'Olahraga'),
        ('SN', 'Seni'),
        ('MS', 'Musik'),
        ('CP', 'Cosplay'),
        ('LG', 'Lingkungan'),
        ('VL', 'Volunteer'),
        ('AK', 'Akademis'),
        ('KL', 'Kuliner'),
        ('PW', 'Pariwisata'),
        ('FS', 'Festival'),
        ('FM', 'Film'),
        ('FN', 'Fashion'),
        ('LN', 'Lainnya')
    ]

    user_profile = UserProfile.objects.all()
    if user_profile.role == "AD":
        form = EventForm(request.POST or None)
        if form.is_valid():
            event_entry = form.save(commit=False)
            event_entry.user = request.user
            event_entry.save()
            return redirect('yogevent:show_main')

        context = {'form': form, "categories":categories}
        return render(request, "create_event_entry.html", context)

    return HttpResponse(b"CREATED", status=201)

@require_POST
def create_event_entry(request):
    user_profile = UserProfile.objects.all()
    if user_profile.role == "AD":
        form = EventForm(request.POST or None)
        if form.is_valid():
            event_entry = form.save(commit=False)
            event_entry.user = request.user
            event_entry.save()
            return redirect('yogevent:show_main')

        context = {'form': form}
        return render(request, "create_event_entry.html", context)

    return HttpResponse(b"CREATED", status=201)

def detail_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = getattr(request.user, 'userprofile', None)
    user_profiles = UserProfile.objects.all()

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'image_url': request.image_url if hasattr(request, 'image_url') else None,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'users': user_profiles,
        'event': event,
    }
    return render(request, 'detail_event.html', context)

def delete_event(request, uuid):
    print(f"Edit event called with UUID: {uuid}")
    event = get_object_or_404(Event, uuid=uuid)
    event.delete()
    return HttpResponseRedirect(reverse('yogevent:show_main'))

def edit_event(request, uuid):

    event = get_object_or_404(Event, uuid=uuid)  # Use get_object_or_404 for safety
    form = EventForm(request.POST or None, instance=event)

    if request.method == "POST" and form.is_valid():  # Check method first
        form.save()
        return HttpResponseRedirect(reverse('yogevent:show_main'))
    else:
        print(form.errors)

    context = {'form': form, 'event': event}
    return render(request, "edit_event.html", context)
