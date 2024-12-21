from django import forms
from modules.main.models import Event, EventCategory, Rating, TicketPrice
from django.utils.html import strip_tags
from django import forms
from django.core.exceptions import ValidationError
from datetime import datetime

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'category', 'start_time', 'end_time', 'location', 'image_urls']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm resize-none',
                'required': True
            }),
            'start_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'required': True
            }),
            'end_time': forms.DateTimeInput(attrs={
                'type': 'datetime-local',
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'required': False
            }),
            'category': forms.Select(choices=EventCategory.choices),
            'location': forms.TextInput(attrs={'required': False}),
            'image_urls': forms.URLInput(attrs={'required': False}),
        }

    def clean_datetime(self, datetime_str):
        """Helper method to parse datetime from Flutter"""
        if datetime_str:
            try:
                # Coba parse format ISO
                return datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
            except ValueError:
                try:
                    # Coba parse format datetime-local HTML
                    return datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M')
                except ValueError:
                    raise ValidationError("Invalid datetime format")
        return None

    def clean_start_time(self):
        start_time = self.cleaned_data.get('start_time')
        if isinstance(start_time, str):
            start_time = self.clean_datetime(start_time)
        return start_time

    def clean_end_time(self):
        end_time = self.cleaned_data.get('end_time')
        if end_time:
            if isinstance(end_time, str):
                end_time = self.clean_datetime(end_time)
        return end_time

    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time:
            if end_time <= start_time:
                self.add_error('end_time', "End time must be after start time")

        return cleaned_data
    
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