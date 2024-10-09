import json
from django.core.management.base import BaseCommand
from main.models import *

class Command(BaseCommand):
    help = 'Seed data from json file'
    
    def handle(self, *args, **kwargs):
        with open('event-dataset.json', 'r') as file:
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
                