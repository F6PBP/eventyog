from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from modules.main.models import MerchCart, EventCart
from eventyog.decorators import check_user_profile
from django.http import JsonResponse
from django.views.decorators.http import require_POST

@check_user_profile(is_redirect=False)
def main(request: HttpRequest) -> HttpResponse:
    
    # Retrieve cart items for events and merchandise
    cart_events = EventCart.objects.filter(user=request.user)
    cart_merch = MerchCart.objects.filter(user=request.user)

    # Calculate cumulative total price
    priceEvent = 0
    priceCart = 0
    for i in cart_events:
        priceEvent += i.totalPrice()
    
    for i in cart_merch:
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
    }

    return render(request, 'cart.html', context)

@require_POST
def update_cart(request, type, item_id, action):
    user = request.user

    # Fetch the correct cart item based on type
    if type == 'event':
        try:
            cart_item = EventCart.objects.get(id=item_id, user=user)
        except EventCart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Event item not found.'})
    elif type == 'merch':
        try:
            cart_item = MerchCart.objects.get(id=item_id, user=user)
        except MerchCart.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Merch item not found.'})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid cart item type.'})

    # Update quantity based on action
    if action == 'increase':
        cart_item.quantity += 1
    elif action == 'decrease' and cart_item.quantity > 0:
        cart_item.quantity -= 1
    else:
        return JsonResponse({'success': False, 'error': 'Invalid action or minimum quantity reached.'})

    # Save the updated cart item
    cart_item.save()

    # Calculate the total price for this cart item (quantity * price)
    item_total_price = cart_item.totalPrice()  # Assuming you have a method totalPrice on the cart item models

    # Recalculate the total price for all cart items for the user
    cart_events = EventCart.objects.filter(user=user)
    cart_merch = MerchCart.objects.filter(user=user)

    # Summing up total price for all events and merchandise items
    total_price = sum([event.totalPrice() for event in cart_events]) + \
                  sum([merch.totalPrice() for merch in cart_merch])              

    # Return the updated values in the response
    return JsonResponse({
        'success': True,
        'new_quantity': cart_item.quantity,  # Updated quantity of the specific item
        'item_total_price': item_total_price,  # Total price of this specific item
        'total_price': total_price  # Total price of the entire cart
    })