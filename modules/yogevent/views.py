from django.shortcuts import get_object_or_404, render, redirect, reverse
from modules.yogevent.forms import EventForm, RatingForm
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
    events = Event.objects.all()
    query = request.GET.get('q')
    category = request.GET.get('category')

    if query:
        events = events.filter(Q(title__icontains=query))

    if category:
        events = events.filter(category=category)

    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.user_profile.role == 'AD',
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
    title = strip_tags(request.POST.get('title'))
    description = strip_tags(request.POST.get('description'))
    category = request.POST.get('category')
    start_time = request.POST.get('start_time')
    end_time = request.POST.get('end_time', '')
    location = strip_tags(request.POST.get('location'))
    image_url = strip_tags(request.POST.get('image_url'))

    end_time = end_time if end_time != "" else None
    if end_time and start_time >= end_time:
        context = {
            'message': 'Tidak Bisa Membuat Event karena Acara Berakhir sebelum Dimulai',
        }
        return render(request, "error.html", context)

    try:
        print(f"Creating event with title: {title}")
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
        
        return JsonResponse({'status': 'success', 'redirect_url': reverse('yogevent:main')})
    
    except Exception as e:
        print(f"Error creating event: {e}")
        context = {
            'message': 'Error',
        }
        return render(request, "error.html", context)


def detail_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = getattr(request.user, 'userprofile', None)
    merchandise = Merchandise.objects.all()

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'image_url': request.image_url if hasattr(request, 'image_url') else None,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'event': event,
        'merchandise': merchandise,
    }
    return render(request, 'detail_event.html', context)

def delete_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    event.delete()
    return HttpResponseRedirect(reverse('yogevent:main'))

def edit_event(request, uuid):

    event = get_object_or_404(Event, uuid=uuid)  # Use get_object_or_404 for safety
    form = EventForm(request.POST or None, instance=event)

    if request.method == "POST" and form.is_valid():  # Check method first
        form.save()
        return HttpResponseRedirect(reverse('yogevent:main'))

    context = {
        'user': request.user,
        'show_navbar': True,
        'show_footer': True,
        'event': event,
        'form': form,
    }

    return render(request, "edit_event.html", context)

def rate_event(request, event_id):
    event = Event.objects.get(pk=event_id)
    total_rating = event.user_rating.aggregate(Avg('rating'))
    # average_rating = Rating.objects.filter(event=event).aggregate(Avg('rating'))['rating__avg']

    total_rating_value = total_rating['rating__avg'] or 0
    # print(f"Total Rating Value: {total_rating_value}")  # Debugging line

    context = {
        'user': request.user,
        'show_navbar': True,
        'show_footer': True,
        'event': event,
        'total_rating': total_rating_value,
    }
    
    return render(request, 'detail_event.html', context)

def add_rating(request, event_id):
    if request.method == 'POST':
        rating_value = request.POST.get('rating')
        event = get_object_or_404(Event, pk=event_id)

        # Debugging output
        print(f"Received rating for event {event.title}: {rating_value}")

        try:
            rating_value = int(rating_value)  # Convert to integer
            if rating_value < 1 or rating_value > 5:  # Assuming a 1-5 rating scale
                print("Rating value out of bounds.")
                return redirect('yogevent:rate_event', event_id=event_id)
        except (ValueError, TypeError):
            print("Invalid rating value.")
            return redirect('yogevent:rate_event', event_id=event_id)

        # Create the rating
        rating = Rating.objects.create(user=request.user.userprofile, rated_event=event, rating=rating_value)

        # Check if the rating was created
        print(f"Rating created: {rating.rating} for event {event.title} by user {request.user.username}")

        return redirect('yogevent:rate_event', event_id=event_id)
