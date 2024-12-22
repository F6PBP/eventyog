from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from modules.main.models import MerchCart, EventCart, UserProfile, Event, Merchandise
from eventyog.decorators import check_user_profile
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json

@check_user_profile(is_redirect=False)
def main(request: HttpRequest) -> HttpResponse:
    # Retrieve cart items for events and merchandise
    cart_events = EventCart.objects.filter(user=request.user)
    cart_merch = MerchCart.objects.filter(user=request.user)
    user_profile = UserProfile.objects.get(user=request.user)

    # Get the merchandise the user has bought
    buyedM = user_profile.boughtMerch.all()

    # Calculate cumulative total price
    priceEvent = 0
    priceCart = 0
    for i in cart_events:
        if i.ticket.event.image_urls:
            i.image_url = i.ticket.event.image_urls
        else:
            i.image_url = 'https://media-cldnry.s-nbcnews.com/image/upload/t_fit-760w,f_auto,q_auto:best/rockcms/2024-06/240602-concert-fans-stock-vl-1023a-9b4766.jpg'
        priceEvent += i.totalPrice()
    
    for i in cart_merch:
        i.image_url = i.merchandise.image_url
        priceCart += i.totalPrice()
    
    total_price = priceEvent + priceCart

    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
        'cart_events': cart_events,        # Pass events cart items
        'cart_merch': cart_merch,          # Pass merchandise cart items
        'total_price': total_price,        # Pass cumulative total price
        'remaining_balance': user_profile.wallet - total_price
    }

    return render(request, 'cart.html', context)

@require_POST
@transaction.atomic
def checkout(request):
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    # Parse updated quantities from the request
    data = json.loads(request.body)
    updated_events = data.get('event', {})
    updated_merch = data.get('merch', {})

    # Calculate total cart price
    total_price = sum(1 * item['pricePerItem'] for item in updated_events.values()) + \
                  sum(item['quantity'] * item['pricePerItem'] for item in updated_merch.values())

    # Check if the wallet has enough balance
    if user_profile.wallet < total_price:
        return JsonResponse({'success': False, 'error': 'Insufficient wallet balance.'})

    # Update cart items
    cart_events = EventCart.objects.filter(user=user)
    cart_merch = MerchCart.objects.filter(user=user)
    
    # Reduce merchandise quantity
    for item in updated_merch.values():
        merch = Merchandise.objects.get(id=item['id'])
        merch.quantity -= item['quantity']
        merch.save()
    
    # Empty cart
    cart_events.delete()
    cart_merch.delete()

    # Deduct total price from wallet and save
    user_profile.wallet -= total_price
    user_profile.save()

    # Return success response with updated wallet balance
    return JsonResponse({'success': True, 'new_wallet_balance': user_profile.wallet})

@check_user_profile()
def empty_cart(request):
    user = request.user
    cart_events = EventCart.objects.filter(user=user)
    cart_merch = MerchCart.objects.filter(user=user)

    cart_events.delete()
    cart_merch.delete()

    return JsonResponse({'success': True})