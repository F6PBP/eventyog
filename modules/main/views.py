from django.shortcuts import render, HttpResponse
from django.contrib.auth.decorators import login_required

# Create your views here.
@login_required(login_url='auth:login')
def main(request):
    return render(request, 'base.html', {'show_navbar': True, 'show_footer': True})

def about(request):
    return render(request, 'about-us.html', {'show_navbar': True, 'show_footer': True})