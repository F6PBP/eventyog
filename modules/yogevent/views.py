from django.utils import timezone
from datetime import datetime
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect, reverse
from modules.yogevent.forms import EventForm, TicketPriceForm
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from modules.main.models import *
from eventyog.decorators import check_user_profile
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.db.models import Q
from django.db.models import Avg
from django.shortcuts import redirect
import json

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
            event.image_urls = 'https://via.placeholder.com/'
        
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
    
    for category in categories:
        temp.append({
            'code': category[0],
            'name': category[1]
        })
        
    categories = temp
    
    events_list = []
    for event in events:
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

    end_time = end_time if end_time else None

    if not title or not category or not start_time:
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
    ratings = Rating.objects.filter(rated_event=event)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    merchandise = Merchandise.objects.all()
    
    # See all ticket
    tickets = TicketPrice.objects.filter(event=event)
    tickets = tickets if len(tickets) > 0 else None

    # Remove tickets with 0 price
    if tickets:
        tickets = tickets.exclude(price=0)
    
    ratings = Rating.objects.filter(rated_event=event)
    
    total_rating = 0
    
    if len(ratings) > 0:
        for rating in ratings:
            total_rating += rating.rating
        total_rating = total_rating / len(ratings)

    registered_event = user_profile.registeredEvent.all()
    
    is_booked = False
    for ticket in registered_event:
        if ticket.event == event:
            is_booked = True
            break
    
    # Check if user has given the rating
    rating = Rating.objects.filter(user=user_profile, rated_event=event)
    
    first_rating = None
    if rating.exists():
        is_rated = True
        first_rating = rating.first()
    else:
        is_rated = False
        
    # Check if this event already in user cart
    event_cart = EventCart.objects.filter(user=request.user)
    
    is_in_cart = False
    
    for cart in event_cart:
        if cart.ticket.event == event:
            is_in_cart = True
            
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'image_url': user_profile.profile_picture,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'event': event,
        'average_rating': round(average_rating, 1),
        'merchandise': merchandise,
        'tickets': tickets,
        'total_rating': total_rating,
        'is_booked': is_booked,
        'is_in_cart': is_in_cart,
        'is_rated': is_rated,
        'first_rating': first_rating,
        'is_in_cart': is_in_cart,
    }
    return render(request, 'detail_event.html', context)

@check_user_profile(is_redirect=True)
@csrf_exempt
@require_POST
def book_event(request):
    event_id = request.POST.get('event_uuid')
    ticket_name = request.POST.get('ticket_name')
    
    event = Event.objects.get(uuid=event_id)
    
    tickets = TicketPrice.objects.filter(event=event)
    user_profile = request.user_profile
    
    # See all ticket
    tickets = TicketPrice.objects.filter(event=event)
    tickets = tickets.exclude(price=0)
    
    if (len(tickets) == 0):
        tickets = None
    
    # If tickets is None then event is free
    if tickets is None:
        new_free_ticket = TicketPrice(
            name='Free Ticket',
            price=0,
            event=event
        )
        
        new_free_ticket.save()
        
        user_profile.registeredEvent.add(new_free_ticket)
    else:
        # If tickets is not None then event is not free
        ticket = TicketPrice.objects.filter(name=ticket_name).first()
        event_cart = EventCart(user=request.user,  ticket=ticket)
        event_cart.save()

    return JsonResponse({'status': True, 'message': 'Event booked successfully.'})            


@check_user_profile()
@csrf_exempt
@require_POST
def cancel_book(request):
    body = request.body.decode('utf-8')
    # body = json.loads(body)
    
    event_id = request.POST.get('event_uuid')
    event = get_object_or_404(Event, uuid=event_id)
    user_profile = request.user_profile
    
    registered_ticket = user_profile.registeredEvent.filter(event=event)
    
    if registered_ticket.exists():
        for ticket in registered_ticket:
            user_profile.registeredEvent.remove(ticket)
        return JsonResponse({'status': True, 'message': 'Event booking cancelled successfully.'})
        
    return JsonResponse({'status': True, 'message': 'Event cancelled successfully.'})

def delete_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    event.delete()
    return HttpResponseRedirect(reverse('yogevent:main'))

def edit_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid) 
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == "POST":  
        event.title = strip_tags(request.POST.get('title'))
        event.description = strip_tags(request.POST.get('description'))
        event.category = request.POST.get('category')
        event.start_time = request.POST.get('start_time')
        event.end_time = request.POST.get('end_time', '')
        event.location = strip_tags(request.POST.get('location'))
        event.image_urls = [request.POST.get('image_url')]
        event.end_time = event.end_time if event.end_time != "" else None


        if event.image_urls == [""]:
            event.image_urls = []

        if event.title == "" or event.category == "":
            return render(request, "error.html", {
                "message":"judul atau kategori tidak boleh kosong",
                'user': request.user,
                'user_profile': user_profile,
                'image_url': user_profile.profile_picture,
                'show_navbar': True,
                'show_footer': True,
                'is_admin': user_profile.role == 'AD' if user_profile else False,
                })

        if event.end_time and event.start_time >= event.end_time:
            return render(request, "error.html", {
                "message":"Acara berakhir sebelum dimulai.",
                'user': request.user,
                'user_profile': user_profile,
                'image_url': user_profile.profile_picture,
                'show_navbar': True,
                'show_footer': True,
                'is_admin': user_profile.role == 'AD' if user_profile else False,
                })
        
        event.save()
        return HttpResponseRedirect(reverse('yogevent:detail_event', args=[event.uuid]))

    if (len(event.image_urls) == 0 ):
        event.image_urls = ""
        
    event.CATEGORY_CHOICES = EventCategory.choices
    event.start_time = event.start_time.strftime('%Y-%m-%dT%H:%M')
    event.end_time = event.end_time.strftime('%Y-%m-%dT%H:%M') if event.end_time else ""
    
    context = {
        'user': request.user,
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'event': event,
    }

    return render(request, "edit_event.html", context)

@check_user_profile(is_redirect=True)
@require_POST
@csrf_exempt
def add_rating(request, event_id):
    event = get_object_or_404(Event, uuid=event_id)
    rating_value = request.POST.get('rating')
    review = request.POST.get('review', '')
    user_profile = getattr(request.user, 'userprofile', None)

    try:
        rating_value = int(rating_value)
    except ValueError:
        return JsonResponse({"status" : False, 'error': 'Invalid rating input'}, status=400)

    # Create and save the new rating
    new_rating = Rating(
        user=user_profile, 
        rated_event=event, 
        rating=rating_value, 
        review=review
    )
    new_rating.save()
    average_rating = Rating.objects.filter(rated_event=event).aggregate(Avg('rating'))['rating__avg']
    context = {
        'average_rating': round(average_rating, 1),
    }
    return JsonResponse({'status': True, 'message': 'Rating submitted successfully!', "data": context})

def create_rating_event(request, event_id): #Kemungkinan akan dihapus tapi keep dulu
    event = get_object_or_404(Event, uuid=event_id)
    average_rating = Rating.objects.filter(rated_event=event).aggregate(Avg('rating'))['rating__avg'] or 0
    user_profile = getattr(request.user, 'userprofile', None)

    return render(request, 'create_rating_event.html', {
        'user': request.user,
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True,
        'event': event,
        'average_rating': round(average_rating, 1),
    })

def get_rating_event(request, event_uuid):
    event = get_object_or_404(Event, uuid=event_uuid)
    average_rating = Rating.objects.filter(rated_event=event).aggregate(Avg('rating'))['rating__avg'] or 0
    user_profile = UserProfile.objects.get(user=request.user)

    context = {
        'user_name': user_profile.user.username, 
        'average_rating': round(average_rating, 1),
    }

    return JsonResponse({'status': True, 'message': 'Rating submitted successfully!', "data": context})

def load_event_ratings(request, event_id):
    event = get_object_or_404(Event, uuid=event_id)
    
    # Get all ratings for the event and calculate the average rating
    ratings = Rating.objects.filter(rated_event=event).values("rating", "review")
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    # Return the ratings data as JSON
    return JsonResponse({
        "average_rating": round(average_rating, 1),
        "ratings": list(ratings),
    })

@csrf_exempt
def ticket_price_list(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    ticket_prices = TicketPrice.objects.filter(event=event)

    context = {
        'event': event,
        'ticket_prices': ticket_prices,
    }
    return render(request, 'ticket_price_list.html', context)

def add_ticket_price(request, event_id):
    event = get_object_or_404(Event, id=event_id)

    if request.method == 'POST':
        form = TicketPriceForm(request.POST)
        if form.is_valid():
            ticket_price = form.save(commit=False)
            ticket_price.event = event
            ticket_price.save()
            return redirect('ticket_price_list', event_id=event.id)
    else:
        form = TicketPriceForm()

    context = {
        'event': event,
        'form': form,
    }
    return render(request, 'add_ticket_price.html', context)

@check_user_profile()
def buy_ticket(request):
    body = request.body.decode('utf-8')
    body = json.loads(body)
    
    ticket_id = body['ticket_id']
    ticket = TicketPrice.objects.get(id=ticket_id)    
    
    user = request.user
    
    # Add to EventCart
    # Check if the ticket is already in the event cart
    if not EventCart.objects.filter(user=user, ticket=ticket).exists():
        event_cart = EventCart(user=user, ticket=ticket)
        event_cart.save()
    else:
        return JsonResponse({'status': False, 'message': 'Ticket already in cart.'})
    
    return JsonResponse({'status': True, 'message': 'Ticket bought successfully.'})

