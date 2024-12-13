from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from .forms import MerchandiseForm
from modules.main.models import Merchandise, Event, MerchCart
from django.urls import reverse
from django.http import HttpResponseRedirect
from eventyog.decorators import check_user_profile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core import serializers
from django.http import JsonResponse
import json

@check_user_profile(is_redirect=False)
def main(request: HttpRequest) -> HttpResponse:
    context = {
        'show_navbar': True,
        'is_admin': request.is_admin,
    }
    return render(request, 'merchandise.html', context)

def create_merchandise(request):
    form = MerchandiseForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        merchandise = form.save(commit=False)
        merchandise.user = request.user
        merchandise.save()
        return redirect('merchandise:main')

    context = {
        'form': form,
        'show_navbar': True
    }
    return render(request, "create_merchandise.html", context)

@check_user_profile()
def show_merchandise_by_id(request, id):
    try:
        merch = Merchandise.objects.get(id=id)
    except Merchandise.DoesNotExist:
        return redirect('main:main')
    
    context = {
        'merch': merch,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
    }
    return render(request, "merchandise_detail.html", context)

@csrf_exempt
@require_POST
def create_merchandise_ajax(request):
    name = request.POST.get("name")
    description = request.POST.get("description")
    price = request.POST.get("price")
    image_url = request.POST.get("image_url")
    event_id = request.POST.get("event_id")

    event = Event.objects.get(uuid=event_id)

    new_merchandise = Merchandise(
        name = name, 
        description = description,
        price = price,
        image_url = image_url,
        related_event = event
    )
    new_merchandise.save()

    return JsonResponse({"status": "CREATED"}, status = 201)

def edit_merchandise(request, id):
    merchandise = Merchandise.objects.get(pk = id)
    form = MerchandiseForm(request.POST or None, instance=merchandise)
    
    event = merchandise.related_event

    if form.is_valid() and request.method == "POST":
        form.save()
        return HttpResponseRedirect(reverse('yogevent:detail_event', args=[merchandise.related_event.uuid]))

    context = {
        'form': form,
        'show_navbar': True
    }
    return render(request, "edit_merchandise.html", context)

def delete_merchandise(request, id):
    merchandise = Merchandise.objects.get(pk = id)
    merchandise.delete()
    return HttpResponseRedirect(reverse('yogevent:detail_event', args=[merchandise.related_event.uuid]))

@check_user_profile()
def showMerch_json(request, event_id: str):
    event = Event.objects.get(uuid=event_id)
    data = Merchandise.objects.filter(related_event=event).order_by('created_at')[::-1]
    
    merch_cart = MerchCart.objects.filter(user=request.user)
    
    temp = []
    
    
    
    for merch in data:
        bought_quantity = 0
        for cart_item in merch_cart:
            if cart_item.merchandise.id == merch.id:
                bought_quantity = cart_item.quantity
                break

        temp.append({
            'pk': merch.id,
            'name': merch.name,
            'quantity': merch.quantity,
            'description': merch.description,
            'price': merch.price,
            'image_url': merch.image_url,
            'bought_quantity': bought_quantity,
            'created_at': merch.created_at.isoformat(),
            'updated_at': merch.updated_at.isoformat(),
            'related_event': merch.related_event.uuid
        })

    return JsonResponse(temp, safe=False)


@check_user_profile()
def add_items_to_cart(request):
    
    items = json.loads(request.body)['items']
    merch_cart = MerchCart.objects.filter(user=request.user)
    
    for item in items:
        merch = Merchandise.objects.get(pk=item['id'])
        
        for cart_item in merch_cart:
            if cart_item.merchandise.id == merch.id:
                cart_item.quantity = item['quantity']
                cart_item.save()
                break
        else:
            new_cart_item = MerchCart(
                user=request.user,
                merchandise=merch,
                quantity=item['quantity']
            )
            new_cart_item.save()
            
    return JsonResponse({"status": "OK"}, status=200)