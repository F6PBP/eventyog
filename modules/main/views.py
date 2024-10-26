from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
from eventyog.decorators import check_user_profile
from .models import Event

# Create your views here.
@check_user_profile(is_redirect=False)
def main(request):
    faq_qna = [
        {
            'id': 1,
            'question': 'What is EventYog?',
            'answer': 'EventYog is an online event management platform that allows you to create and manage events, sell tickets, and track registrations. It is a one-stop solution for all your event management needs.'
        },
        {
            'id': 2,
            'question': 'How do I create an event?',
            'answer': 'To create an event, you need to sign up and log in to your account. Once you are logged in, you can create an event by clicking on the "Create Event" button on the dashboard.'
        },
        {
            'id': 3,
            'question': 'How do I sell tickets for my event?',
            'answer': 'You can sell tickets for your event by setting up ticket types, pricing, and availability. You can also customize the ticketing process by adding discount codes, promo codes, and more.'
        },
        {
            'id': 4,
            'question': 'How do I track registrations for my event?',
            'answer': 'You can track registrations for your event by viewing the event dashboard. The dashboard provides real-time data on ticket sales, registrations, and more.'
        },
    ]
    
    first_8_events = Event.objects.all()[:8]
    
    for event in first_8_events:
        if event.image_urls:
            event.image_urls = event.image_urls[0]
        else:
            event.image_urls = 'https://via.placeholder.com/800x400'
            
        event.month = event.start_time.strftime('%b').upper()
        event.day = event.start_time.strftime('%d')
    
    
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_footer': True,
        'is_admin': request.is_admin,
        'faq_qna': faq_qna,
        'isDark': True,
        'first_8_events': first_8_events,
    }
    
    return render(request, 'landing.html', context)

@check_user_profile(is_redirect=False)
def about(request):
    context = {
        'user': request.user,
        'user_profile': request.user_profile,
        'image_url': request.image_url,
        'show_navbar': True,
        'show_footer': True,
        'is_admin': request.is_admin,
    }
    return render(request, 'about-us.html', context)