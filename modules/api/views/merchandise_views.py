from  django.http import HttpRequest, JsonResponse
from modules.api.ApiResponse import ApiResponse
from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from modules.merchandise.forms import MerchandiseForm
from modules.main.models import Merchandise, Event, MerchCart
from django.urls import reverse
from django.http import HttpResponseRedirect
from eventyog.decorators import check_user_profile_api
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core import serializers
from django.http import JsonResponse
import json

def main(request: HttpRequest) -> JsonResponse:
    context = {
        'show_navbar': True,
        'is_admin': getattr(request, 'is_admin', False),  # Default False jika tidak ada atribut
    }
    return JsonResponse(context, status=200)

@csrf_exempt
@check_user_profile_api()
def show_merchandise_by_id(request, id):
    try:
        merch = Merchandise.objects.get(id=id)
    except Merchandise.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Merchandise not found"}, status=404)

    context = {
        'id': merch.id,
        'name': merch.name,
        'description': merch.description,
        'price': merch.price,
        'image_url': merch.image_url,
        'quantity': merch.quantity,
        'related_event': merch.related_event.uuid,
        'created_at': merch.created_at.isoformat(),
        'updated_at': merch.updated_at.isoformat(),
    }
    return JsonResponse({"status": "success", "data": context, "is_admin": request.is_admin}, status=200)

@csrf_exempt
@require_POST
def create_merchandise_ajax(request):
    try:
        data = json.loads(request.body)
        event = Event.objects.get(uuid=data["event_id"])

        if int(data["quantity"]) <= 0:
            return JsonResponse({"status": "error", "message": "Quantity must be greater than zero"}, status=400)
        if float(data["price"]) <= 0:
            return JsonResponse({"status": "error", "message": "Price must be greater than zero"}, status=400)

        new_merchandise = Merchandise.objects.create(
            name=data["name"],
            description=data["description"],
            price=data["price"],
            image_url=data["image_url"],
            related_event=event,
            quantity=data["quantity"]
        )

        response = {
            "status": "success",
            "message": "Merchandise created successfully",
            "data": {
                "id": new_merchandise.id,
                "name": new_merchandise.name,
                "description": new_merchandise.description,
                "price": new_merchandise.price,
                "image_url": new_merchandise.image_url,
                "quantity": new_merchandise.quantity,
                "related_event": new_merchandise.related_event.uuid,
                "created_at": new_merchandise.created_at.isoformat(),
                "updated_at": new_merchandise.updated_at.isoformat(),
            }
        }
        return JsonResponse(response, status=201)

    except Event.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Event not found"}, status=404)
    except KeyError as e:
        return JsonResponse({"status": "error", "message": f"Missing field: {str(e)}"}, status=400)

@csrf_exempt
def edit_merchandise(request, id):
    try:
        merchandise = Merchandise.objects.get(pk=id)
        data = json.loads(request.body)

        if int(data.get("quantity", merchandise.quantity)) <= 0:
            return JsonResponse({"status": "error", "message": "Quantity must be greater than zero"}, status=400)
        if float(data.get("price", merchandise.price)) <= 0:
            return JsonResponse({"status": "error", "message": "Price must be greater than zero"}, status=400)

        # Update the merchandise fields
        merchandise.name = data.get("name", merchandise.name)
        merchandise.description = data.get("description", merchandise.description)
        merchandise.price = data.get("price", merchandise.price)
        merchandise.image_url = data.get("image_url", merchandise.image_url)
        merchandise.quantity = data.get("quantity", merchandise.quantity)
        merchandise.save()

        response = {
            "status": "success",
            "message": "Merchandise updated successfully",
            "data": {
                "id": merchandise.id,
                "name": merchandise.name,
                "description": merchandise.description,
                "price": merchandise.price,
                "image_url": merchandise.image_url,
                "quantity": merchandise.quantity,
                "related_event": merchandise.related_event.uuid,
                "created_at": merchandise.created_at.isoformat(),
                "updated_at": merchandise.updated_at.isoformat(),
            }
        }
        return JsonResponse(response, status=200)
    except Merchandise.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Merchandise not found"}, status=404)

@csrf_exempt
def delete_merchandise(request, id):
    try:
        merchandise = Merchandise.objects.get(pk=id)
        merchandise.delete()
        return JsonResponse({"status": "success", "message": "Merchandise deleted successfully"}, status=200)
    except Merchandise.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Merchandise not found"}, status=404)

@check_user_profile_api()
def showMerch_json(request, event_id: str):
    
    try:
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

        return JsonResponse({
            "status": "success",
            "data": temp,
            "is_admin": request.is_admin  # Default False if attribute does not exist
        }, status=200)
    except Event.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Event not found"}, status=404)

@check_user_profile_api()
@csrf_exempt
def add_items_to_cart(request):
    try:
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
                
        return JsonResponse({"status": "success", "message": "Items added to cart successfully", "is_admin": request.is_admin}, status=200)
    except Merchandise.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Merchandise not found"}, status=404)
    except KeyError as e:
        return JsonResponse({"status": "error", "message": f"Missing field: {str(e)}"}, status=400)