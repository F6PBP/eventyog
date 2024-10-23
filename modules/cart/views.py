from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from modules.main.models import MerchCart, EventCart
from eventyog.decorators import check_user_profile

@check_user_profile(is_redirect=False)
def main(request: HttpRequest) -> HttpResponse:
    cart_event = EventCart.objects.filter(user=request.user)
    merch_event = MerchCart.objects.filter(user=request.user)
    return render(request, 'cart.html')