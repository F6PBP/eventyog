from django import forms
from modules.main.models import Event, EventCategory, Rating, TicketPrice
from django.utils.html import strip_tags

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'start_time', 'end_time', 'location', 'image_urls']
        widgets = {
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'category': forms.Select(choices=EventCategory.choices),
            'image_urls': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Paste image URLs as JSON'}),
        }
    
    def clean_title(self):
        title = self.cleaned_data["title"]
        return strip_tags(title)
    
    def clean_description(self):
        description = self.cleaned_data["description"]
        return strip_tags(description)
    
    def clean_location(self):
        location = self.cleaned_data["location"]
        return strip_tags(location)

class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['rating', 'review']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'review': forms.Textarea(attrs={'rows': 3}),
        }

class TicketPriceForm(forms.ModelForm):
    class Meta:
        model = TicketPrice
        fields = ['name', 'price']
        labels = {
            'name': 'Ticket Name',
            'price': 'Ticket Price',
        }

class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=100)