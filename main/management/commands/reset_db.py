import json
from django.core.management.base import BaseCommand
from main.models import *

class Command(BaseCommand):
    help = 'Seed data from json file'
    
    def handle(self, *args, **kwargs):
        # Delete All Event data
        Event.objects.all().delete()     
        TicketPrice.objects.all().delete()
        
        # Delete All Merchandise data
        Merchandise.objects.all().delete()