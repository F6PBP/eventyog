from datetime import datetime
import json
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect, reverse
from modules.yogevent.forms import EventForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from modules.main.models import *
from eventyog.decorators import check_user_profile
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.db.models import Avg
from django.shortcuts import redirect

@check_user_profile(is_redirect=True)
def main(request: HttpRequest) -> HttpResponse:
    user_profile = UserProfile.objects.get(user=request.user)
    events = Event.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        events = events.filter(Q(title__icontains=query))

    if category:
        events = events.filter(category=category)

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'events': events,
    }
    return render(request, 'yogevent.html', context)

def show_event_xml(request):    
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile:
        events = Event.objects.filter(userprofile=user_profile)
    else:
        events = Event.objects.all()

    return HttpResponse(serializers.serialize("xml", events), content_type="application/json") 

def show_event_json(request):
    user_profile = UserProfile.objects.get(user=request.user)
    if user_profile:
        events = Event.objects.filter(userprofile=user_profile)
    else:
        events = Event.objects.all()

    return HttpResponse(serializers.serialize("json", events), content_type="application/json") 

def show_xml_event_by_id(request, id):
    data = Event.objects.filter(pk=id)  # Cari event berdasarkan primary key
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_event_by_id(request, id):
    data = Event.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

@check_user_profile(is_redirect=True)
@csrf_exempt
@require_POST
def create_event_entry_ajax(request):
    title = strip_tags(request.POST.get('title'))
    description = strip_tags(request.POST.get('description'))
    category = request.POST.get('category')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time', '')
    location = strip_tags(request.POST.get('location'))
    image_url = strip_tags(request.POST.get('image_url'))

    end_time = end_time if end_time != "" else None

    if title == "" or description == "" or location == "" or image_url == "":
        return JsonResponse({'status': False, 'message': 'Invalid input'})

    if end_time and start_time >= end_time:
        return JsonResponse({'status': False, 'message': 'Acara berakhir sebelum dimulai.'})

    try:
        new_event = Event(
            title=title,
            description=description,
            category=category,
            start_time=start_time,
            end_time=end_time,
            location=location,
            image_urls=[image_url]
        )
        new_event.save()
        return JsonResponse({'status': True, 'message': 'Event created successfully.'})
    
    except Exception as e:
        return JsonResponse({'status': False, 'message': 'Error creating event.'})


def detail_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = UserProfile.objects.get(user=request.user)

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'event': event,
    }
    return render(request, 'detail_event.html', context)

def delete_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    event.delete()
    return HttpResponseRedirect(reverse('yogevent:main'))

def edit_event(request, uuid):

    event = get_object_or_404(Event, uuid=uuid) 
    user_profile = UserProfile.objects.get(user=request.user)
    form = EventForm(request.POST or None, instance=event)

    if request.method == "POST" and form.is_valid():  
        form.save()
        return HttpResponseRedirect(reverse('yogevent:main'))

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True,
        'event': event,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'form': form,
    }

    return render(request, "edit_event.html", context)

def add_rating(request, event_id):
    event = get_object_or_404(Event, uuid=event_id)

    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        review = request.POST.get('review', '')
        user_profile = UserProfile.objects.get(user=request.user)

        # Validate rating value
        try:
            rating_value = int(rating_value)
        except (ValueError, TypeError):
            messages.error(request, 'Invalid rating value.')
            return redirect('yogevent:create_rating_event', event_id=event.uuid)

        # Create and save the new rating
        new_rating = Rating(user=user_profile, rated_event=event, rating=rating_value, review=review)
        new_rating.save()
        messages.success(request, 'Rating added successfully!')
        average_rating = Rating.objects.filter(rated_event=event).aggregate(Avg('rating'))['rating__avg'] or 1

        print(event.title)
        for rate in Rating.objects.filter(rated_event=event):
            print(rate)
        print(" ")
        print(average_rating, len(Rating.objects.filter(rated_event=event)))

        context = {
            'user': request.user,
            'user_profile': user_profile,
            'show_navbar': True,
            'show_footer': True,
            'event': event,
            'total_rating': average_rating,
        }
        print(context['total_rating'])

        return render(request, 'detail_event.html', context)
    return redirect('yogevent:create_rating_event', event_id=event.uuid)

def event_list(request):
    events = Event.objects.all()
    data = []
    for event in events:
        rating_count = Rating.objects.filter(event=event).count()
        avg_rating = 0
        if rating_count > 0:
            total_rating = 0
            ratings = Rating.objects.filter(event=event)
            for rating in ratings:
                total_rating += rating.rating
            avg_rating = total_rating / rating_count
        data.append({
            'id': event.id,
            'name': event.name,
            'location': event.location,
            'date': event.date,
            'rating_count': rating_count,
            'avg_rating': avg_rating,
        })
    return JsonResponse({'events': data})


def create_rating_event(request, event_id):
    event = get_object_or_404(Event, uuid=event_id)
    return render(request, 'create_rating_event.html', {'event': event})