from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField
import uuid

class UserRoles(models.TextChoices):
    ADMIN='AD', 'Admin',
    USER='US', 'User',
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    bio = models.TextField()
    profile_picture = CloudinaryField('image')
    categories = models.CharField(max_length=200)
    
    registeredEvent = models.ManyToManyField('Event', blank=True)
    boughtMerch = models.ManyToManyField('Merchandise', blank=True)
    
    friends = models.ManyToManyField('UserProfile', blank=True)
    
    role = models.CharField(
        choices=UserRoles.choices,
        default=UserRoles.USER,
        max_length=2
    )
    
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
    event = models.ForeignKey('Event', on_delete=models.CASCADE, related_name='ticketPrice')
    
    def isFree(self):
        return self.price == 0

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rated_event = models.ForeignKey('Event', on_delete=models.CASCADE)
    rating = models.IntegerField()
    review = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
class PostImage(models.Model):
    image = CloudinaryField('image')
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    images = models.ManyToManyField(PostImage, blank=True)
    related_event = models.ForeignKey('Event', on_delete=models.CASCADE, null=True)
    last_update = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0)
    description = models.TextField(null=True, blank=True)
    comments = models.ManyToManyField('PostComment', blank=True)
    
class PostComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    last_update = models.DateTimeField(auto_now=True)
    like = models.IntegerField(default=0)
    reply_to = models.ForeignKey('PostComment', on_delete=models.CASCADE, null=True)

class Event(models.Model):
    uuid = models.UUIDField(primary_key=True, editable=False, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    category = models.CharField(
        choices=EventCategory.choices,
        default=EventCategory.LAINNYA,
        max_length=2
    )
    
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(null=True, blank=True)
    
    location = models.CharField(max_length=200, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    merch = models.ManyToManyField('Merchandise', blank=True)
    
    user_rating = models.ManyToManyField(Rating, blank=True)
    

class Merchandise(models.Model):
    merchId = models.AutoField(primary_key=True)
    image_url = models.URLField()
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)