import json
from django.core.management.base import BaseCommand
from modules.main.models import *
import os
import random
import shutil
from dotenv import load_dotenv


class Command(BaseCommand):
    help = 'Seed data from json file'
    path = 'dataset/'
    
    def seed_event(self):
        with open(f'{self.path}event-dataset.json', 'r', errors='ignore') as file:
            data = json.load(file)
            for row in data:
                try:
                    category = EventCategory.LAINNYA

                    # Check if category exists
                    if row['category'] in dict(EventCategory.choices):
                        category = row['category']
                        
                    image_urls = row.get('image_urls', [])
                        
                    event = Event.objects.create(
                        title=row['name'],
                        description=row['description'],
                        category=category,
                        start_time=row['startDate'],
                        end_time=row['endDate'],
                        location=row['location'],
                        image_urls=image_urls
                    )
                    
                    event.save()
                    
                    # Create ticket price
                    if row['ticket'] is not None:    
                        for price in row['ticket']:
                            if price is not None:
                                price = TicketPrice.objects.create(
                                    name=price['type'],
                                    price=price['price'],
                                    event=event
                                )
                                price.save()
                except Exception as e:
                    print('Error in row' + str(row['name']))
                    print(e)
                    pass
        
        print('Seeding event done')
        
    def seed_merch(self):
        with open(f'{self.path}product-dataset.json', 'r', errors='ignore') as file:
            data = json.load(file)
            for row in data:
                try:
                    merch = Merchandise.objects.create(
                        image_url=row['image_url'],
                        name=row['name'],
                        description=row['description'],
                        price=row['price'],
                    )
                    merch.save()
                except Exception as e:
                    print(e)
                    print('Error in row' + str(row))
                    
        print('Seeding merch done')
    
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
            with open(f'{self.path}user.json', 'r', errors='ignore') as file:
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
            
        dekdepe = UserProfile.objects.get(user__username='dekdepe')
        
        # Make dekdepe as admin
        dekdepe.role = "AD"
        
        dekdepe.save()
        
        print('Seeding user done')
    
    def seed_user_merch_and_event(self):
        # Seed all user with 10 first event
        users = UserProfile.objects.all()
        
        dekdepe = UserProfile.objects.get(user__username='dekdepe')
        
        # Seed MerchCart
        for user in users:
            for merch in Merchandise.objects.all()[:10]:
                merchcart = MerchCart.objects.create(
                    user=user.user,
                    merchandise=merch,
                    quantity=1
                )
                
                merchcart.save()
                
        # Seed EventCart
        for user in users:
            for event in TicketPrice.objects.all()[:5]:
                eventcart = EventCart.objects.create(
                    user=user.user,
                    ticket=event,
                    quantity=1
                )
                
                eventcart.save()
        
        for user in users:
            for merch in Merchandise.objects.all()[:10]:
                user.boughtMerch.add(merch)
            for event in Event.objects.all()[:10]:
                user.registeredEvent.add(event)
            user.save()
            
        print('Seeding user merch and event done')
    
    def seed_rating(self):
        events = Event.objects.all()
        dekdepe = UserProfile.objects.get(user__username='dekdepe')
        
        for event in events:
            rating = Rating.objects.create(
                user=dekdepe,
                rated_event=event,
                rating=random.randint(1, 5),
                review='Good event for everyone'
            )
            rating.save()        
        
        print('Seeding rating done')
            
    def seed_forum(self):
        dekdepe = UserProfile.objects.get(user__username='dekdepe')
        users = UserProfile.objects.all()
        
        for i in range(10):
            try:
                forum = Forum.objects.create(
                    user=users[random.randint(0, len(users) - 1)],
                    title=f'Forum {i}',
                    content=f'Description {i}',
                )
                forum.save()
                
                for j in range(10):
                    comment = ForumReply.objects.create(
                        user=users[random.randint(0, len(users) - 1)],                        
                        forum=forum,
                        content=f'Comment {j} in forum {i}'
                    )
                    comment.save()
                    
                    # Add Nested Comment
                    for k in range(3):
                        nested_comment = ForumReply.objects.create(
                            user=users[random.randint(0, len(users) - 1)],                        
                            forum=forum,
                            content=f'Nested Comment {k} in comment {j} in forum {i}',
                            reply_to=comment
                        )
                        nested_comment.save()
            except Exception as e:
                print('Error seeding forum: ', e)
                    
        print('Seeding forum done')
            
    def setup(self):
                    # Print os path
            print(os.getcwd())
            
            load_dotenv()
            
            PRODUCTION = os.getenv('PRODUCTION') == 'True'
            
            # Remove db sqlite3
            if os.path.exists('db.sqlite3'):
                os.remove('db.sqlite3')
                
            # Delete Migrations File
            try:
                shutil.rmtree('modules/main/migrations')
            except:
                pass
            
            if not PRODUCTION:
                os.system('python manage.py makemigrations main')
                os.system('python manage.py migrate main')
                os.system('python manage.py migrate')
            else:        
                os.system('python manage.py makemigrations')
                os.system('python manage.py migrate')
            
            print('Migrate done')
            
    def handle(self, *args, **options):
        try:
            print('Seeding data...')
            self.setup()
            os.system('python manage.py reset_db')
            self.seed_event()
            self.seed_merch()
            self.seed_user()
            self.seed_user_merch_and_event()
            self.seed_rating()
            self.seed_forum()
            
            os.system('python manage.py runserver')
        except KeyboardInterrupt:
            print('Exiting...')
            pass
        except Exception as e:
            print('Error: ', e)
            pass