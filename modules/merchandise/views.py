from django.shortcuts import render,redirect
from django.http import HttpRequest, HttpResponse
from .forms import MerchandiseForm
from modules.main.models import Merchandise
from django.urls import reverse
from django.http import HttpResponseRedirect

def main(request: HttpRequest) -> HttpResponse:
    context = {
        'show_navbar': True,
        'is_admin': getattr(request, 'is_admin', True)
    }
    return render(request, 'merchandise.html', context)

def create_merchandise(request):
    form = MerchandiseForm(request.POST or None)

    if form.is_valid() and request.method == "POST":
        merchandise = form.save(commit=False)
        merchandise.user = request.user
        merchandise.save()
        return redirect('main:main')

    context = {
        'form': form,
        'show_navbar': True
    }
    return render(request, "create_merchandise.html", context)

def edit_merchandise(request, id):
    merchandise = Merchandise.objects.get(pk = id)
    form = MerchandiseForm(request.POST or None, instance=merchandise)

    if form.is_valid() and request.method == "POST":
        form.save()
        return HttpResponseRedirect(reverse('main:main'))

    context = {'form': form}
    return render(request, "edit_merchandise.html", context)

def delete_merchandise(request, id):
    merchandise = Merchandise.objects.get(pk = id)
    merchandise.delete()
    return HttpResponseRedirect(reverse('main:main'))