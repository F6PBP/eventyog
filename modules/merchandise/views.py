from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from .forms import MerchandiseForm
from modules.main.models import Merchandise, Event
from django.urls import reverse
from django.http import HttpResponseRedirect
from eventyog.decorators import check_user_profile
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.core import serializers

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

    new_merchandise = Merchandise(
        name = name, 
        description = description,
        price = price,
        image_url = image_url,
    )
    new_merchandise.save()

    return HttpResponse(b"CREATED", status=201)

def edit_merchandise(request, id):
    merchandise = Merchandise.objects.get(pk = id)
    form = MerchandiseForm(request.POST or None, instance=merchandise)

    if form.is_valid() and request.method == "POST":
        form.save()
        return HttpResponseRedirect(reverse('merchandise:main'))

    context = {
        'form': form,
        'show_navbar': True
    }
    return render(request, "edit_merchandise.html", context)

def delete_merchandise(request, id):
    merchandise = Merchandise.objects.get(pk = id)
    merchandise.delete()
    return HttpResponseRedirect(reverse('main:main'))

def showMerch_json(request):
    data = Merchandise.objects.all()
    return HttpResponse(serializers.serialize("json", data), content_type="application/json")
