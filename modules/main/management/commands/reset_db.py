from django.core.management.base import BaseCommand
from modules.main.models import *

class Command(BaseCommand):
    help = 'Seed data from json file'
    
    def handle(self, *args, **kwargs):
        UserProfile.objects.all().delete()
        User.objects.all().delete()
        
        Merchandise.objects.all().delete()
        TicketPrice.objects.all().delete()
        
        # Delete All Event data
        Event.objects.all().delete()     
 
        EventCart.objects.all().delete()
        MerchCart.objects.all().delete()
        
        Forum.objects.all().delete()
        ForumReply.objects.all().delete()
        
        Rating.objects.all().delete()       
        
        print('Reset database done')
        
        input('Press any key to continue...')