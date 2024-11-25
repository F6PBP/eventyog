from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import transaction
import json

from modules.main.models import UserProfile, EventCart, MerchCart, Merchandise
from eventyog.decorators import check_user_profile

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


@require_POST
@transaction.atomic
def checkout(request):
    """
    API untuk memproses checkout barang di keranjang.
    """
    user = request.user
    user_profile = UserProfile.objects.get(user=user)

    try:
        data = json.loads(request.body)
        updated_events = data.get('event', {})
        updated_merch = data.get('merch', {})

        total_price = sum(item['pricePerItem'] for item in updated_events.values()) + \
                      sum(item['quantity'] * item['pricePerItem'] for item in updated_merch.values())

        # Periksa saldo dompet cukup atau tidak
        if user_profile.wallet < total_price:
            return JsonResponse({'success': False, 'error': 'Insufficient wallet balance.'})

        # Perbarui kuantitas merchandise
        for item in updated_merch.values():
            merch = Merchandise.objects.get(id=item['id'])
            merch.quantity -= item['quantity']
            merch.save()

        # Hapus item dari keranjang setelah checkout
        EventCart.objects.filter(user=user).delete()
        MerchCart.objects.filter(user=user).delete()

        # Kurangi saldo dompet pengguna
        user_profile.wallet -= total_price
        user_profile.save()

        return JsonResponse({'success': True, 'new_wallet_balance': user_profile.wallet})

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
@transaction.atomic
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
