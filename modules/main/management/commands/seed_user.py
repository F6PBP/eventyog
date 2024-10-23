import json
from django.core.management.base import BaseCommand
from modules.main.models import *

class Command(BaseCommand):
    help = 'Seed data from json file'
    path = 'dataset/'
    
    def seed_user(self):
        # Create Super User
        user = User.objects.create_user(
            username='admin',
            password='123',
            is_superuser=True,
            is_staff=True
        )
        user.save()
        
        try:
            data = []
            with open(f'{self.path}user.json', 'r') as file:
                data = json.load(file)
            
            for row in data:
                user = User.objects.filter(username=row['username'])
                if len(user) == 0:
                    print(f'Creating user {row['username']}')
                    user = User.objects.create_user(
                        username=row['username'],
                        password=row['password'],   
                    )
                    user.save()
                
                user = User.objects.get(username=row['username'])    
                user_profile = UserProfile.objects.create(
                    user=user,
                    name=row['name'],
                    email=row['email'],
                    bio=row['bio'],
                    categories='',
                )
                events = Event.objects.all() [:10]
                for event in events:
                    user_profile.registeredEvent.add(event)
                    
                user.save()
        except Exception as e:
            print('Error seeding user: ', e)
        
    def handle(self, *args, **kwargs):
        self.seed_user()