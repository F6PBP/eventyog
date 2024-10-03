from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField()
    email = models.EmailField()
    
    registeredEvent = models.ManyToManyField('Event', blank=True)
    boughtMerch = models.ManyToManyField('Merchandise', blank=True)
    
    def __str__(self):
        return self.user.username

# Class for Event Category
class EventCategory(models.TextChoices):
    OLAHRAGA='OL', 'Olahraga',
    SENI='SN', 'Seni',
    MUSIK='MS', 'Musik',
    COSPLAY='CP', 'Cosplay',
    LINGKUNGAN='LG', 'Lingkungan',
    VOLUNTEER='VL', 'Volunteer',
    LAINNYA='LN', 'Lainnya'

class TicketPrice(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    def isFree(self):
        return self.price == 0

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rated_event = models.ForeignKey('Event', on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(
        choices=EventCategory.choices,
        default=EventCategory.LAINNYA,
        max_length=2
    )
    
    ticketPrice = models.ForeignKey(TicketPrice, on_delete=models.CASCADE)    
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    merch = models.ManyToManyField('Merchandise', blank=True)
    
    user_rating = models.ManyToManyField(Rating, blank=True)
    

class Merchandise(models.Model):
    merchId = models.AutoField(primary_key=True)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class Post (models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey('Event', on_delete=models.CASCADE)
    
    reply = models.ManyToManyField('Post', blank=True)