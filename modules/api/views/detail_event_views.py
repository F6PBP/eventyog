import json
import uuid
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from modules.main.models import Rating, Event, EventCart, TicketPrice
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Avg

@csrf_exempt
def add_rating(request, event_id: uuid.UUID):
    print("\nDebug Rating : ")
    print(f"LAGI DIAKSES SAMA USER : {request.user.username}")
    print(f"Method {request.method}")

    try:
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'Please login first'}, status=401)

        try:
            event = Event.objects.get(uuid=event_id)
            user_profile = request.user.userprofile
        except Event.DoesNotExist:
            return JsonResponse({'error': 'Event not found'}, status=404)

        # Handle GET request to fetch ratings
        if request.method == 'GET':
            # Get all ratings using related_name if defined in Rating model
            ratings = Rating.objects.filter(rated_event=event)
            
            print(f"Debug Get - Ratings queryset: {ratings}")  # Debug print
            

            # Calculate average rating
            if ratings.exists():
                avg_rating = ratings.aggregate(Avg('rating'))['rating__avg']
                avg_rating = round(float(avg_rating), 1)  # Round to 1 decimal place
            else:
                avg_rating = 0.0

            print(f"Total ratings: {ratings.count()}")
            print(f"Average rating: {avg_rating}")

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
            
            print(f"Debug - Response data: {response_data}")  # Debug print
            
            return JsonResponse(response_data)

        elif request.method == 'POST':
            try:
                # Ubah dari json.loads ke request.POST
                print("Received POST data:", request.POST)
                rating_value = request.POST.get('rating')
                review = request.POST.get('review', '').strip()
                print(f"Received rating data: rating={rating_value}, review={review}")

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
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'Please login first'}, status=401)
    try:
        event = Event.objects.get(uuid=event_id)
        tickets = TicketPrice.objects.filter(event=event)
        
        ticket_data = [{
            'id': ticket.id,
            'name': ticket.name,
            'price': float(ticket.price),
            'is_free': ticket.isFree()
        } for ticket in tickets]
        
        return JsonResponse({
            'status': 'success',
            'tickets': ticket_data
        })
    except Event.DoesNotExist:
        print(f"Debug - Event not found: {event_id}")
        return JsonResponse({'error': 'Event not found'}, status=404)
    except Exception as e:
        print(f"Debug - Error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@login_required
@require_POST
def buy_ticket_flutter(request):
    try:
        # Debug prints
        print("Request POST:", request.POST)
        print("Request body:", request.body)
        
        # Coba ambil ticket_id dari POST data dulu
        ticket_id = request.POST.get('ticket_id')
        
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
        
        event_cart = EventCart(user=user, ticket=ticket)
        event_cart.save()
        return JsonResponse(
            {
                'status': True,
                'message': 'Ticket successfully added to cart!',
            },
            status=201
        )
            
    except Exception as e:
        print("Error:", str(e))
        return JsonResponse(
            {'status': False, 'message': str(e)},
            status=500
        )
    
@csrf_exempt
def delete_user_ticket(request):
    if request.method == 'POST':
        try:
            # Get ticket_id from POST data
            ticket_id = request.POST.get('ticket_id')
            print(f"Attempting to delete cart with ID: {ticket_id}")
            
            # Print existing carts for debugging
            existing_carts = EventCart.objects.filter(user=request.user)
            for cart in existing_carts:
                print(f"Cart ID: {cart.id}, Event: {cart.ticket.event.title}")

            try:
                # Get the cart item first to ensure it exists
                cart_item = EventCart.objects.get(
                    id=ticket_id,
                    user=request.user
                )
                
                # Delete the cart item
                cart_item.delete()
                
                print(f"Successfully deleted cart item {ticket_id}")
                return JsonResponse(
                    {
                        'status': True,
                        'message': 'Ticket removed from cart successfully'
                    },
                    status=200
                )
                
            except EventCart.DoesNotExist:
                print(f"Cart item {ticket_id} not found")
                return JsonResponse(
                    {
                        'status': False,
                        'message': 'Ticket not found in cart'
                    },
                    status=404
                )
                
        except Exception as e:
            print(f"Error deleting cart item: {str(e)}")
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
        
        # Get cart item for this event
        cart_item = EventCart.objects.filter(
            user=user,
            ticket__event=event
        ).first()
        
        has_ticket = cart_item is not None
        
        # Check if user has rated
        has_rated = Rating.objects.filter(
            user=user.userprofile,
            rated_event=event
        ).exists()
        
        # Include ticket data if exists
        ticket_data = None
        if cart_item:
            ticket_data = {
                'id': cart_item.ticket.id,
                'name': cart_item.ticket.name,
                'price': float(cart_item.ticket.price),
                'cart_id': cart_item.id
            }
        
        return JsonResponse({
            'status': 'success',
            'has_ticket': has_ticket,
            'has_rated': has_rated,
            'ticket': ticket_data  # Include ticket data in response
        })
        
    except Event.DoesNotExist:
        return JsonResponse({
            'error': 'Event not found'
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=500)

# Optional: Add a view to get cart items for an event
@csrf_exempt
def get_user_event_cart(request, event_id):
    try:
        event = Event.objects.get(uuid=event_id)
        cart_items = EventCart.objects.filter(
            user=request.user,
            ticket__event=event
        )
        
        return JsonResponse({
            'status': True,
            'has_ticket': cart_items.exists(),
            'cart_items': [{
                'id': item.id,
                'ticket_name': item.ticket.name,
                'price': float(item.ticket.price),
                'is_free': item.ticket.isFree()
            } for item in cart_items]
        })
    except Event.DoesNotExist:
        return JsonResponse({
            'status': False,
            'message': 'Event not found'
        })
    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': str(e)
        })
    
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