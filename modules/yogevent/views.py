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
from django.core.paginator import Paginator

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
        
    for event in events:
        # Set image urls 
        if event.image_urls:
            event.image_urls = event.image_urls[0]
        else:
            event.image_urls = 'https://via.placeholder.com/800x400'
        
        event.month = event.start_time.strftime('%B')
        event.day = event.start_time.strftime('%d')
        
        rating_count = Rating.objects.filter(rated_event=event).count()
        avg_rating = 0
        if rating_count > 0:
            total_rating = 0
            ratings = Rating.objects.filter(rated_event=event)
            for rating in ratings:
                total_rating += rating.rating
            avg_rating = total_rating / rating_count
        event.total_rating = avg_rating
        
    categories = EventCategory.choices
    temp = []
    
    for category in categories:
        temp.append({
            'code': category[0],
            'name': category[1]
        })
        
    categories = temp
    

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'events': events,
        'categories': categories,
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

def get_events_by_queries(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    start_time = request.GET.get('start_date')
    end_time = request.GET.get('end_date')
    page = int(request.GET.get('page', 1))
    limit = int(request.GET.get('limit', 10))
    
    print(f"Query: {query}, Category: {category}, Start Time: {start_time}, End Time: {end_time}, Page: {page}, Limit: {limit}")
    
    events = Event.objects.all()
    
    if query:
        events = events.filter(Q(title__icontains=query))
        
    if category:
        events = events.filter(category=category)
        
    if start_time:
        events = events.filter(start_time__gte=start_time)
    
    if end_time:
        events = events.filter(end_time__lte=end_time)

    for event in events:
        # Set image urls 
        if event.image_urls:
            event.image_urls = event.image_urls[0]
        else:
            event.image_urls = 'https://via.placeholder.com/800x400'
        
        event.month = event.start_time.strftime('%B')
        event.day = event.start_time.strftime('%d')
        
        rating_count = Rating.objects.filter(rated_event=event).count()
        avg_rating = 0
        if rating_count > 0:
            total_rating = 0
            ratings = Rating.objects.filter(rated_event=event)
            for rating in ratings:
                total_rating += rating.rating
            avg_rating = total_rating / rating_count
        event.total_rating = avg_rating
        
    categories = EventCategory.choices
    temp = []
    
    paginator = Paginator(events, limit)
    paginated_events = paginator.get_page(page)
    
    print(paginated_events.object_list)
    
    for category in categories:
        temp.append({
            'code': category[0],
            'name': category[1]
        })
        
    categories = temp
    
    events_list = []
    for event in paginated_events.object_list:
        events_list.append({
            'uuid': event.uuid,
            'title': event.title,
            'description': event.description,
            'category': event.category,
            'start_time': event.start_time,
            'end_time': event.end_time,
            'location': event.location,
            'image_urls': event.image_urls,
            'month': event.month,
            'day': event.day,
            'total_rating': event.total_rating,
        })

    response = {
        'events': events_list,
        'total': paginator.count,
        'page': paginated_events.number,
        'num_pages': paginator.num_pages,
    }
    
    return JsonResponse(response)

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
        return JsonResponse({'status': True, 'message': 'Event created successfully.'})
    
    except Exception as e:
        return JsonResponse({'status': False, 'message': 'Error creating event.'})

def detail_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = UserProfile.objects.get(user=request.user)
    merchandise = Merchandise.objects.all()
    
    # See all ticket
    tickets = TicketPrice.objects.filter(event=event)

    if (len(tickets) == 0):
        tickets = None
        
    ratings = Rating.objects.filter(rated_event=event)
    
    total_rating = 0
    
    if len(ratings) > 0:
        for rating in ratings:
            total_rating += rating.rating
        total_rating = total_rating / len(ratings)
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'event': event,
        'merchandise': merchandise,
        'tickets': tickets,
        'total_rating': total_rating,
    }
    return render(request, 'detail_event.html', context)

@check_user_profile(is_redirect=True)
@csrf_exempt
@require_POST
def book_event(request):
    event_id = request.POST.get('event_uuid')
    ticket_name = request.POST.get('ticket_name')
    
    event = get_object_or_404(Event, uuid=event_id)
    tickets = TicketPrice.objects.filter(event=event)
    user_profile = request.userprofile
    
    # See all ticket
    tickets = TicketPrice.objects.filter(event=event)

    if (len(tickets) == 0):
        tickets = None
    
    # If tickets is None then event is free
    if tickets is None:
        user_profile.registered_event.add(event)
    else:
        # If tickets is not None then event is not free
        ticket = get_object_or_404(TicketPrice, name=ticket_name)
        event_cart = EventCart(user=user_profile, event=event, ticket=ticket)
        event_cart.save()

    return JsonResponse({'status': True, 'message': 'Event booked successfully.'})            

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