import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from modules.main.models import Rating, Event, EventCart, TicketPrice
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

@csrf_exempt
@login_required
def create_rating_flutter(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event.objects.get(title=data["event"])  # Assuming event title is unique
        new_rating = Rating.objects.create(
            user=request.user,
            event=event,
            rating=data["rating"],
            review=data["review"],
        )
        new_rating.save()
        return JsonResponse({"status": "success"}, status=200)
    else:
        return JsonResponse({"status": "error"}, status=401)
    
@csrf_exempt
@login_required
@require_POST
def buy_ticket_flutter(request):
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