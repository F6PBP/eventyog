from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse, HttpRequest
from django.shortcuts import render
from eventyog.decorators import check_user_profile
from eventyog.types import AuthRequest

@login_required(login_url='auth:login')
@check_user_profile(is_redirect=True)
def main(request: AuthRequest) -> HttpResponse:
    registered_events = request.user_profile.registeredEvent.all()
    
    registered_events = [
        event.event for event in registered_events
    ]    
    
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

@login_required(login_url='auth:login')
@check_user_profile()
def fetch_registered_event(request: HttpRequest) -> JsonResponse:
    start_time = request.GET.get('start_time')
    registered_events = request.user_profile.registeredEvent.all()
    
    registered_events = [
        event.event for event in registered_events
    ]

    if start_time:
        registered_events = registered_events.filter(start_time__gte=start_time)
    
    event_list = []
    for event in registered_events:
        event_list.append({
            'uuid': event.uuid,
            'title': event.title,
            'description': event.description,
            'month': event.start_time.strftime('%b'),
            'day': event.start_time.strftime('%d'),
            'location': event.location,
            'image_urls': event.image_urls or ['default_image_url'],
        })
    
    return JsonResponse({'events': event_list})