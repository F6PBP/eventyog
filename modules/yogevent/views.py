from django.shortcuts import get_object_or_404, render, reverse
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from modules.yogevent.forms import EventForm
from modules.main.models import *
from eventyog.decorators import check_user_profile
from django.core import serializers
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.html import strip_tags
from django.db.models import Avg
import json
from datetime import datetime

@check_user_profile(is_redirect=True)
def main(request: HttpRequest) -> HttpResponse:
    user_profile = UserProfile.objects.get(user=request.user)
    events = Event.objects.all()
    categories = [{"code": code, "name": name} for code, name in EventCategory.choices]
    
    for event in events:
        # Set image urls 
        if not event.image_urls:
            print(event.title)
            event.image_urls = 'https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/rockcms/2024-06/240602-concert-fans-stock-vl-1023a-9b4766.jpg'
        
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
    events = Event.objects.all()
    return HttpResponse(serializers.serialize("xml", events), content_type="application/json") 

def show_event_json(request):
    events = Event.objects.all()
    return HttpResponse(serializers.serialize("json", events), content_type="application/json") 

def show_xml_event_by_id(request, id):
    data = Event.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("xml", data), content_type="application/xml")

def show_json_event_by_id(request, id):
    data = Event.objects.filter(pk=id)
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")

def get_events_by_queries(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    events = Event.objects.all()
    
    if query and not category:
        events = events.filter(title__icontains=query)
    elif category and not query:
        events = events.filter(category=category)
    elif query and category:
        events = events.filter(
            title__icontains=query,
            category=category
        )

    for event in events:
        if not event.image_urls:
            event.image_urls = 'https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/rockcms/2024-06/240602-concert-fans-stock-vl-1023a-9b4766.jpg'

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

def create_event_entry_ajax(request):
    try:
        # Get data from request
        title = strip_tags(request.POST.get('title', '').strip())
        description = strip_tags(request.POST.get('description', '').strip())
        category = request.POST.get('category')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time', None)  # Explicitly set default to None
        location = strip_tags(request.POST.get('location', '').strip())
        image_url = request.POST.get('image_url', '').strip()

        # Required fields validation
        if not title:
            return JsonResponse({
                'status': False,
                'field': 'title',
                'message': 'Title is required'
            })
            
        if not description:
            return JsonResponse({
                'status': False,
                'field': 'description',
                'message': 'Description is required'
            })

        if not start_time:
            return JsonResponse({
                'status': False,
                'field': 'start_time',
                'message': 'Start time is required'
            })

        # Handle end_time - only try to parse if it's not empty
        end_time_parsed = None
        if end_time and end_time.strip():  # Check if end_time exists and is not just whitespace
            try:
                start_time_dt = datetime.strptime(start_time, '%Y-%m-%dT%H:%M')
                end_time_dt = datetime.strptime(end_time, '%Y-%m-%dT%H:%M')
                
                if start_time_dt >= end_time_dt:
                    return JsonResponse({
                        'status': False,
                        'field': 'end_time',
                        'message': 'End time must be later than start time'
                    })
                end_time_parsed = end_time
            except ValueError:
                return JsonResponse({
                    'status': False,
                    'field': 'end_time',
                    'message': 'Invalid end time format'
                })

        # Create event object with cleaned data
        new_event = Event.objects.create(
            title=title,
            description=description,
            category=category,
            start_time=start_time,
            end_time=end_time_parsed,  # This will be None if end_time was empty
            location=location if location else None,
            image_urls=image_url if image_url else None
        )

        return JsonResponse({
            'status': True,
            'message': 'Event created successfully',
            'event_uuid': str(new_event.uuid)  # Return the UUID of created event
        })
    
    except Exception as e:
        print(f"Debug - Error creating event: {str(e)}")  # Debug print
        print(f"Debug - Request POST data: {request.POST}")  # Debug print
        return JsonResponse({
            'status': False,
            'message': f'Error creating event: {str(e)}'
        })
    
@check_user_profile(is_redirect=False)
def detail_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = getattr(request.user, 'userprofile', None)
    ratings = Rating.objects.filter(rated_event=event)
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0
    merchandise = Merchandise.objects.all()
    tickets = TicketPrice.objects.filter(event=event)
    tickets = tickets if len(tickets) > 0 else None
    registered_event = user_profile.registeredEvent.all()
    
    if not event.image_urls:
        event.image_urls = 'https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/rockcms/2024-06/240602-concert-fans-stock-vl-1023a-9b4766.jpg'

    if tickets:
        tickets = tickets.exclude(price=0)
    
    ratings = Rating.objects.filter(rated_event=event)
    
    total_rating = 0
    
    if len(ratings) > 0:
        for rating in ratings:
            total_rating += rating.rating
        total_rating = total_rating / len(ratings)

    
    is_booked = False
    for ticket in registered_event:
        if ticket.event == event:
            is_booked = True
            break
    
    # Check if user has given the rating
    rating = Rating.objects.filter(user=user_profile, rated_event=event)
    
    is_rated = False
    first_rating = None
    if user_profile:
        user_rating = ratings.filter(user=user_profile).first()
        is_rated = user_rating is not None
        first_rating = user_rating
        
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

@check_user_profile(is_redirect=False)
def edit_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = UserProfile.objects.get(user=request.user)
    
    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            return HttpResponseRedirect(reverse('yogevent:main'))
    else:
        form = EventForm(instance=event)

    context = {
        'user': request.user,
        'user_profile': user_profile,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': user_profile.role == 'AD' if user_profile else False,
        'form': form,
        'event': event
    }

    return render(request, "edit_event.html", context)

@check_user_profile(is_redirect=True)
@require_POST
def add_rating(request, event_id):    
    event = get_object_or_404(Event, uuid=event_id)
    rating_value = request.POST.get('rating')
    review = request.POST.get('review', '')
    user_profile = UserProfile.objects.get(user=request.user)

    if not review:
        return JsonResponse({"status" : False, 'error': 'Please write a review'}, status=400)
    
    try:
        rating_value = int(rating_value)
    except ValueError:
        return JsonResponse({"status" : False, 'error': 'Invalid rating input'}, status=400)
    
    new_rating = Rating(
        user=user_profile, 
        rated_event=event, 
        rating=rating_value, 
        review=review
    )
    new_rating.save()    
    average_rating = Rating.objects.filter(rated_event=event).aggregate(Avg('rating'))['rating__avg']
    rating = Rating.objects.filter(user=user_profile, rated_event=event)
    is_rated = rating.exists()
    first_rating = rating.first()

    context = {
        'average_rating': round(average_rating, 1),
        'is_rated': is_rated,
        'user_rating': {
            'rating': first_rating.rating,
            'review': first_rating.review
        } if first_rating else None
    }
    return JsonResponse({'status': True, 'message': 'Rating submitted successfully!', "data": context})

def get_rating_event(request, uuid):
    event = get_object_or_404(Event, uuid=uuid)
    user_profile = UserProfile.objects.get(user=request.user)

    average_rating = Rating.objects.filter(rated_event=event).aggregate(Avg('rating'))['rating__avg'] or 0
    rating = Rating.objects.filter(user=user_profile, rated_event=event)
    is_rated = rating.exists()
    first_rating = rating.first() if is_rated else None

    # Cek rating dari user yang login
    user_profile = UserProfile.objects.get(user=request.user)
    user_rating = rating.filter(user=user_profile).first()

    context = {
        'user_name': user_profile.user.username, 
        'average_rating': round(average_rating, 1),
        'is_rated': user_rating is not None,  # Lebih eksplisit dalam pengece
        'first_rating': {
            'rating': first_rating.rating,
            'review': first_rating.review
        } if first_rating else None
    }
        
    return JsonResponse({'status': True, 'message': 'Rating submitted successfully!', "data": context})

def load_event_ratings(request, event_id):
    event = get_object_or_404(Event, uuid=event_id)
    ratings = Rating.objects.filter(rated_event=event).values("rating", "review")
    average_rating = ratings.aggregate(Avg('rating'))['rating__avg'] or 0

    user_profile = UserProfile.objects.get(user=request.user)
    rating = Rating.objects.filter(user=user_profile, rated_event=event)
    is_rated = rating.exists()

    return JsonResponse({
        "average_rating": round(average_rating, 1),
        "ratings": list(ratings),
        'is_rated': is_rated
    })

@check_user_profile(is_redirect=True)
def buy_ticket(request):
    body = request.body.decode('utf-8')
    body = json.loads(body)
    
    ticket_id = body['ticket_id']
    ticket = TicketPrice.objects.get(id=ticket_id)    
    
    user = request.user
    
    if not EventCart.objects.filter(user=user, ticket=ticket).exists():
        event_cart = EventCart(user=user, ticket=ticket)
        event_cart.save()
    else:
        return JsonResponse({'status': False, 'message': 'Ticket already in cart.'})
    
    return JsonResponse({'status': True, 'message': 'Ticket bought successfully.'})

