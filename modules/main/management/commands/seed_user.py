import json
from django.core.management.base import BaseCommand
from modules.main.models import *

class Command(BaseCommand):
    help = 'Seed data from json file'
    path = 'dataset/'
    
    def seed_user(self):
        user = User.objects.get(username='dekdepe')
        if user is None:
            user = User.objects.create_user(
                username='dekdepe',
                password='dekdepe',   
            )
            user.save()
            
        user_profile = UserProfile.objects.create(
            user=user,
            name='Dek Depe',
            email='dekdepe@gmail.com',
            bio='Dek Depe is a fictional character',
            categories='',
        )
        events = Event.objects.all() [:10]
        for event in events:
            user_profile.registeredEvent.add(event)
            
        user.save()
        
    def handle(self, *args, **kwargs):
        self.seed_user()