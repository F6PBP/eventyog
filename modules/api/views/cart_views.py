from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.db import transaction
import json
from decimal import Decimal
from django.views.decorators.csrf import csrf_exempt


from modules.main.models import UserProfile, EventCart, MerchCart, Merchandise
from eventyog.decorators import check_user_profile

def decimal_to_float(obj):
    """Rekursif fungsi untuk mengubah Decimal menjadi float dalam JSON response"""
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, list):
        return [decimal_to_float(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: decimal_to_float(v) for k, v in obj.items()}
    return obj


@require_GET
@transaction.atomic
def get_cart_data(request):
    """
    API untuk mengambil data pengguna, keranjang acara, dan keranjang barang dagangan,
    termasuk harga total dan saldo yang tersisa.
    """
    print(request.POST)
    print(request.GET)
    

    try:
        print("berhasil")
        # Ambil data keranjang untuk event dan merchandise
        cart_events = EventCart.objects.filter(user=request.user)
        cart_merch = MerchCart.objects.filter(user=request.user)
        print(cart_events,cart_merch)
        # Ambil profil pengguna
        user_profile = UserProfile.objects.get(user=request.user)
        
        # Hitung total harga
        price_event = sum([event.totalPrice() for event in cart_events])
        price_merch = sum([merch.totalPrice() for merch in cart_merch])
        total_price = price_event + price_merch
        
        # Dapatkan saldo dompet yang tersisa
        remaining_balance = user_profile.wallet - total_price
        
        # Mengembalikan data dalam format JSON
        data = {
            'status': True,
            'message': 'Cart data retrieved successfully.',
            'user_profile': {
                'wallet_balance': float(user_profile.wallet),
            },
            'cart_events': [
                {
                    'image_url': event.ticket.event.image_urls[0] if event.ticket.event.image_urls else None,
                    'title': event.ticket.event.title,
                    'ticket_name': event.ticket.name,
                    'price': float(event.totalPrice()),
                    'quantity': event.quantity
                } for event in cart_events
            ],
            'cart_merch': [
                {
                    'image_url': merch.merchandise.image_url,
                    'name': merch.merchandise.name,
                    'price': float(merch.totalPrice()),
                    'quantity': merch.quantity
                } for merch in cart_merch
            ],
            'total_price': total_price,
            'remaining_balance': remaining_balance
        }
        print(data)
        safe_cart_data = decimal_to_float(data)
        print(safe_cart_data)
        return JsonResponse(safe_cart_data)

    except Exception as e:
        return JsonResponse({
            'status': False,
            'message': f'Error retrieving cart data: {str(e)}'
        })
    
@require_POST
@transaction.atomic
def update_cart(request):
    """
    API untuk memperbarui isi keranjang, termasuk kuantitas dan total harga barang.
    """
    user = request.user

    try:
        data = json.loads(request.body)
        updated_events = data.get('event', {})
        updated_merch = data.get('merch', {})

        cart_events = EventCart.objects.filter(user=user)
        cart_merch = MerchCart.objects.filter(user=user)

        # Perbarui jumlah kuantitas untuk event cart
        for event_id, event_data in updated_events.items():
            event = cart_events.filter(id=event_id).first()
            if event:
                event.quantity = event_data.get('quantity', event.quantity)
                event.save()

        # Perbarui jumlah kuantitas untuk merchandise cart
        for merch_id, merch_data in updated_merch.items():
            merch = cart_merch.filter(id=merch_id).first()
            if merch:
                merch.quantity = merch_data.get('quantity', merch.quantity)
                merch.save()

        return JsonResponse({'success': True, 'message': 'Cart updated successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
@transaction.atomic
def checkout(request):
    """
    API untuk memproses checkout barang di keranjang.
    """
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    try:
        # Parse JSON request body
        data = json.loads(request.body)
        print(f"Received data: {data}")  # Log data yang diterima
        updated_events = data.get('event', [])
        updated_merch = data.get('merch', [])

        # Hitung total harga
        total_price = sum(item['quantity'] * item['pricePerItem'] for item in updated_events) + \
                      sum(item['quantity'] * item['pricePerItem'] for item in updated_merch)
        print(f"Total price: {total_price}, User wallet: {request.user.userprofile.wallet}")

        # Periksa saldo pengguna
        if user_profile.wallet < total_price:
            return JsonResponse({'success': False, 'error': 'Insufficient wallet balance.'})

        EventCart.objects.filter(user=user).delete()
        MerchCart.objects.filter(user=user).delete()
        # Kurangi saldo pengguna
        user_profile.wallet -= total_price
        user_profile.save()

        return JsonResponse({'success': True, 'new_wallet_balance': (user_profile.wallet)})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@csrf_exempt
@require_POST
def empty_cart(request):
    """
    API untuk mengosongkan isi keranjang.
    """
    user = request.user

    try:
        EventCart.objects.filter(user=user).delete()
        MerchCart.objects.filter(user=user).delete()

        return JsonResponse({'success': True, 'message': 'Cart emptied successfully.'})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
