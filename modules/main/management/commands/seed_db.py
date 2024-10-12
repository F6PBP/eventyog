import json
from django.core.management.base import BaseCommand
from modules.main.models import *

class Command(BaseCommand):
    help = 'Seed data from json file'
    path = 'dataset/'
    
    def seed_event(self):
        with open(f'{self.path}event-dataset.json', 'r') as file:
            data = json.load(file)
            for row in data:
                try:
                    category = EventCategory.LAINNYA

                    # Check if category exists
                    if row['category'] in dict(EventCategory.choices):
                        category = row['category']
                        
                    event = Event.objects.create(
                        title=row['name'],
                        description=row['description'],
                        category=category,
                        start_time=row['startDate'],
                        end_time=row['endDate'],
                        location=row['location']
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
                    print('Error in row' + str(row))
                    pass
        
    def seed_merch(self):
        with open(f'{self.path}product-dataset.json', 'r') as file:
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
                    print('Error in row' + str(row))
                    pass
        
    def handle(self, *args, **kwargs):
        self.seed_event()
        self.seed_merch()