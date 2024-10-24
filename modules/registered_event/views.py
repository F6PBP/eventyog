from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from eventyog.decorators import check_user_profile


@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def main(request: HttpRequest) -> HttpResponse:
    print(request)
    registered_events = request.user_profile.registeredEvent.all()
    
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.user_profile.role == 'AD',
        'registered_events': registered_events,
    }
    
    return render(request, 'registered_event.html', context)