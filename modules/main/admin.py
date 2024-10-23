from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(TicketPrice)
admin.site.register(Rating)
admin.site.register(Event)
admin.site.register(Merchandise)
admin.site.register(MerchCart)
admin.site.register(EventCart)