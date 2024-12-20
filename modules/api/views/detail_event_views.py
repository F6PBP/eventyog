import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from modules.main.models import Rating, Event, EventCart, TicketPrice, UserProfile
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Avg

@csrf_exempt
def add_rating(request, event_id: uuid.UUID):
    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=401)

        try:
            event = Event.objects.get(uuid=event_id)
            user_profile = request.user.userprofile
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

        if request.method == 'GET':
            ratings = Rating.objects.filter(rated_event=event)
            # Calculate average rating
            if ratings.exists():
                avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
                avg_rating = round(float(avg_rating), 1)  # Round to 1 decimal place
            else:
                avg_rating = 0.0
            # Format ratings data
            ratings_data = [{
                'username': rating.user.user.username,
                'rating': rating.rating,
                'review': rating.review,
                'created_at': rating.created_at.isoformat()
            } for rating in ratings]
            
            # Get current user's rating if exists
            user_rating = ratings.filter(user=user_profile).first()
            user_rating_data = None
            if user_rating:
                user_rating_data = {
                    'rating': user_rating.rating,
                    'review': user_rating.review
                }

            response_data = {
                'status': 'success',
                'ratings': ratings_data,
                'average_rating': avg_rating,
                'total_ratings': ratings.count(),
                'user_rating': user_rating_data
            }
            return JsonResponse(response_data)

        elif request.method == 'POST':
            try:
                # Ubah dari json.loads ke request.POST
                rating_value = request.POST.get('rating')
                review = request.POST.get('review', '').strip()

                if Rating.objects.filter(user=user_profile, rated_event=event).exists():
                    return JsonResponse({'error': 'You have already rated this event'}, status=400)

                if not review:
                    return JsonResponse({'error': 'Review is required'}, status=400)

                try:
                    rating_value = int(rating_value)
                    if not 1 <= rating_value <= 5:
                        return JsonResponse({'error': 'Rating must be between 1 and 5'}, status=400)
                except (ValueError, TypeError):
                    return JsonResponse({'error': 'Invalid rating value'}, status=400)

                rating, created = Rating.objects.update_or_create(
                    user=user_profile,
                    rated_event=event,
                    defaults={
                        'rating': rating_value,
                        'review': review
                    }
                )

                ratings = Rating.objects.filter(rated_event=event)
                new_avg = ratings.aggregate(Avg('rating'))['rating__avg']
                new_avg = round(float(new_avg), 1)

                return JsonResponse({
                    'status': 'success',
                    'message': 'Rating added successfully',
                    'rating': {
                        'id': rating.id,
                        'rating': rating.rating,
                        'review': rating.review,
                        'username': rating.user.user.username,
                        'created_at': rating.created_at.isoformat()
                    },
                    'new_average': new_avg,
                    'total_ratings': ratings.count()
                })

            except json.JSONDecodeError:
                return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def get_tickets(request, event_id):
    try:
        # print(f"Processing request for event_id: {event_id}")
        event = Event.objects.get(uuid=event_id)
        # print(f"Found event: {event.title}")
        
        # Get all tickets for this event
        tickets = TicketPrice.objects.filter(event=event)
        # print(f"Number of tickets found: {tickets.count()}")
        
        ticket_data = []
        free_ticket_data = None
        
        # Process existing tickets
        for ticket in tickets:
            # print(f"Processing ticket: ID={ticket.id}, Name={ticket.name}, Price={ticket.price}")
            
            # Skip if ticket is invalid
            if ticket.name is None or ticket.price is None:
                print(f"Skipping invalid ticket: {ticket.id}")
                continue
                
            ticket_dict = {
                'id': ticket.id,
                'name': ticket.name or 'Standard Ticket',
                'price': float(ticket.price or 0),
                'is_free': ticket.isFree(),
                'event_title': event.title  # Tambahkan ini
            }
            
            if ticket_dict['is_free']:
                free_ticket_data = ticket_dict
            else:
                ticket_data.append(ticket_dict)
        
        # Add free ticket to list if exists and not already added
        if free_ticket_data and free_ticket_data not in ticket_data:
            # print("Adding existing free ticket to list")
            ticket_data.append(free_ticket_data)
        
        # Create new free ticket if no tickets exist
        if not ticket_data:
            # print("No valid tickets found, creating free ticket")
            try:
                new_free_ticket = TicketPrice.objects.create(
                    name='Free Ticket',
                    price=0,
                    event=event
                )
                # print(f"Created new free ticket with ID: {new_free_ticket.id}")

                ticket_dict = {
                    'id': new_free_ticket.id,
                    'name': new_free_ticket.name,
                    'price': float(new_free_ticket.price),
                    'is_free': True
                }
                ticket_data.append(ticket_dict)
            except Exception as e:
                # print(f"Error creating free ticket: {str(e)}")
                # Continue without creating free ticket if there's an error
                pass

        # Final debug information
        # print("Final ticket data:")
        # for ticket in ticket_data:
        #     print(f"Ticket ID: {ticket['id']}, Name: {ticket['name']}, Price: {ticket['price']}, Is Free: {ticket['is_free']}")

        return JsonResponse({
            'status': 'success',
            'tickets': ticket_data
        })
        
    except Event.DoesNotExist as e:
        print(f"Event not found error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': 'Event not found'
        }, status=404)
        
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'An error occurred: {str(e)}'
        }, status=500)

@csrf_exempt
@login_required
@require_POST
def buy_ticket_flutter(request):
    try:
        # Coba ambil ticket_id dari POST data dulu
        print("Lagi belanja")
        ticket_id = request.POST.get('ticket_id')
        print(ticket_id)
        
        # Jika tidak ada di POST, coba parse dari JSON body
        if not ticket_id:
            try:
                body = request.body.decode('utf-8')
                data = json.loads(body)
                ticket_id = data.get('ticket_id')
            except json.JSONDecodeError:
                # Jika JSON decode gagal, kembalikan ke POST data
                ticket_id = request.POST.get('ticket_id')

        if not ticket_id:
            return JsonResponse(
                {'status': False, 'message': 'No ticket ID provided'},
                status=400
            )

        try:
            ticket = TicketPrice.objects.get(id=ticket_id)
            event = ticket.event
        except TicketPrice.DoesNotExist:
            return JsonResponse(
                {'status': False, 'message': 'Ticket not found.'},
                status=404
            )
        
        user = request.user
        print(user.username)
        
        if EventCart.objects.filter(
            user=user, 
            ticket__event=event
        ).exists():
            return JsonResponse(
                {
                    'status': False, 
                    'message': 'You already have a ticket for this event in your cart.'
                },
                status=400
            )
        print(ticket)

        event_cart = EventCart(user=user, ticket=ticket)
        try:
            event_cart.save()
            print(f"EventCart saved successfully: {event_cart}")
            print(f"EventCart ID: {event_cart.id}")
        except Exception as e:
            print(f"Failed to save EventCart: {e}")
            return JsonResponse({'status': False, 'message': str(e)}, status=500)

        # Check if the object exists in the database
        print(EventCart.objects.filter(user=user))
        response =  JsonResponse({
            'status': True,
            'message': 'Ticket successfully added to cart!',
            'has_ticket': True,  
            'ticket': {     
                'id': ticket.id,
                'cart_id': event_cart.id,
                'name': ticket.name,
                'price': float(ticket.price),
                'event_title': event.title,
                'is_free': False
            }
        }, status=201)
        print(response)
        return response
            
    except Exception as e:
        return JsonResponse(
            {'status': False, 'message': str(e)},
            status=500
        )
    
@csrf_exempt
def delete_user_ticket(request):
    if request.method == 'POST':
        try:
            print(request.POST.get('ticket_id'))
            print(request.user)

            print(EventCart.objects.all())
            for a in EventCart.objects.all():
                print(a.user.username)
                print(a.ticket)
                print(a.ticket.name)
            
            # Cari cart berdasarkan user dan ticket event yang sedang aktif
            cart_item = EventCart.objects.filter(
                user=request.user,
                ticket_id=request.POST.get('ticket_id')  # ticket_id dari tiket, bukan id cart
            ).first()

            
            if not cart_item:
                return JsonResponse(
                    {
                        'status': False,
                        'message': 'Ticket not found in cart'
                    },
                    status=404
                )

            # Get the event from this cart item
            event = cart_item.ticket.event
            
            # Delete all cart items for this user and event
            EventCart.objects.filter(
                user=request.user,
                ticket__event=event
            ).delete()
            
            return JsonResponse(
                {
                    'status': True,
                    'message': 'Ticket removed from cart successfully'
                },
                status=200
            )
                
        except Exception as e:
            return JsonResponse(
                {
                    'status': False,
                    'message': f'Error deleting ticket: {str(e)}'
                },
                status=500
            )
    
    return JsonResponse(
        {
            'status': False,
            'message': 'Invalid request method'
        },
        status=405
    )

@csrf_exempt
def get_user_ticket_status(request, event_id):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please login first'}, status=401)
        
    try:
        event = Event.objects.get(uuid=event_id)
        user = request.user
        user_profile = user.userprofile
        cart_item = EventCart.objects.filter(user=user, ticket__event=event).first()

        registered_ticket = None
        for ticket in user_profile.registeredEvent.all():
            if ticket.event == event:
                registered_ticket = ticket
                break
        
        has_ticket = cart_item is not None or registered_ticket is not None
        has_rated = Rating.objects.filter(user=user_profile, rated_event=event).exists()

        # Include ticket data if exists
        ticket_data = None
        if cart_item:
            ticket_data = {
                'id': cart_item.ticket.id,
                'name': cart_item.ticket.name,
                'price': float(cart_item.ticket.price),
                'cart_id': cart_item.id,
                'event_title': event.title,
                'is_free': False
            }
        elif registered_ticket:
            ticket_data = {
                'id': registered_ticket.id,
                'ticket_id': registered_ticket.id,
                'name': registered_ticket.name,
                'price': float(registered_ticket.price),
                'event_title': event.title,
                'is_free': True
            }

        response = {
            'status': 'success',
            'has_ticket': has_ticket,
            'has_rated': has_rated,
            'ticket': ticket_data
        }
        return JsonResponse(response)
        
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
    
@csrf_exempt
def get_user_event_tickets(request, event_id):    
    if not request.user.is_authenticated:
        return JsonResponse(
            {'status': False, 'message': 'Please login first'},
            status=401
        )
    
    try:
        event = Event.objects.get(uuid=event_id)
        user_cart_tickets = EventCart.objects.filter(
            user=request.user,
            ticket__event=event
        ).select_related('ticket')
        
        tickets_data = []
        for cart_item in user_cart_tickets:
            ticket_info = {
                'id': cart_item.ticket.id,
                'name': cart_item.ticket.name,
                'price': float(cart_item.ticket.price),
                'is_free': cart_item.ticket.isFree(),
                'cart_id': cart_item.id,
                'created_at': cart_item.created_at.isoformat()
            }
            tickets_data.append(ticket_info)
        
        return JsonResponse({
            'status': True,
            'tickets': tickets_data
        }, status=200)
            
    except Event.DoesNotExist:
        return JsonResponse({
            'status': False,
            'message': 'Event not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': str(e)
        }, status=500)
    
@csrf_exempt
@login_required
@require_POST
def book_free_ticket_flutter(request):
    try:
        ticket_id = request.POST.get('ticket_id')
        
        if not ticket_id:
            try:
                body = request.body.decode('utf-8')
                data = json.loads(body)
                ticket_id = data.get('ticket_id')
            except json.JSONDecodeError:
                ticket_id = request.POST.get('ticket_id')

        if not ticket_id:
            return JsonResponse(
                {'status': False, 'message': 'No ticket ID provided'},
                status=400
            )

        try:
            ticket = TicketPrice.objects.get(id=ticket_id)
            user_profile = UserProfile.objects.get(user=request.user)
            
            # Cek apakah user sudah terdaftar di event
            if ticket in user_profile.registeredEvent.all():
                # Disini kita return data tiket yang sudah ada
                return JsonResponse({
                    'status': True,  # Ubah jadi True karena technically user punya tiketnya
                    'message': 'You have already booked this event.',
                    'has_ticket': True,
                    'ticket': {
                        'ticket_id': str(ticket.id),
                        'name': ticket.name,
                        'price': 0,
                        'event_title': ticket.event.title,
                        'is_free': True
                    }
                }, status=200)
            
            # Jika belum terdaftar, daftarkan
            user_profile.registeredEvent.add(ticket)
            
            return JsonResponse({
                'status': True,
                'message': 'Event booked successfully!',
                'has_ticket': True,
                'ticket': {
                    'ticket_id': str(ticket.id),
                    'name': ticket.name,
                    'price': 0,
                    'event_title': ticket.event.title,
                    'is_free': True
                }
            }, status=201)
                
        except TicketPrice.DoesNotExist:
            return JsonResponse(
                {'status': False, 'message': 'Ticket not found'},
                status=404
            )
            
    except Exception as e:
        return JsonResponse(
            {'status': False, 'message': str(e)},
            status=500
        )

@csrf_exempt
@login_required
def cancel_free_booking(request):
    if request.method == 'POST':
        try:
            ticket_id = request.POST.get('ticket_id')
            
            if not ticket_id:
                try:
                    body = request.body.decode('utf-8')
                    data = json.loads(body)
                    ticket_id = data.get('ticket_id')
                except json.JSONDecodeError:
                    pass

            if not ticket_id:
                return JsonResponse(
                    {'status': False, 'message': 'No ticket ID provided'},
                    status=400
                )

            try:
                ticket = TicketPrice.objects.get(id=ticket_id)
            except TicketPrice.DoesNotExist:
                return JsonResponse(
                    {'status': False, 'message': 'Ticket not found'},
                    status=404
                )

            if not ticket.isFree():
                return JsonResponse(
                    {'status': False, 'message': 'This is not a free ticket'},
                    status=400
                )

            user_profile = UserProfile.objects.get(user=request.user)
            
            if ticket not in user_profile.registeredEvent.all():
                return JsonResponse(
                    {'status': False, 'message': 'You have not booked this event'},
                    status=404
                )

            # Hapus dari registeredEvent
            user_profile.registeredEvent.remove(ticket)
            
            return JsonResponse({
                'status': True,
                'message': 'Event booking cancelled successfully',
            }, status=200)
                
        except Exception as e:
            return JsonResponse(
                {'status': False, 'message': f'Error: {str(e)}'},
                status=500
            )
    
    return JsonResponse(
        {'status': False, 'message': 'Invalid request method'},
        status=405
    )