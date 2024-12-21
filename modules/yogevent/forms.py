from django import forms
from modules.main.models import Event, EventCategory, Rating, TicketPrice
from django.utils.html import strip_tags

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
            'category': forms.Select(
                choices=EventCategory.choices,
                attrs={
                    'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                    'required': True
                }
            ),
            'location': forms.TextInput(attrs={
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm',
                'required': False
            }),
            'image_urls': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Paste image URL',
                'class': 'w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm resize-none',
                'required': False
            }),
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        category = cleaned_data.get('category')
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        # Validate required fields
        if not title:
            raise forms.ValidationError("Title is required")
        
        if not category:
            raise forms.ValidationError("Category is required")
            
        if not start_time:
            raise forms.ValidationError("Start time is required")

        # Validate end_time if provided
        if end_time and start_time and end_time <= start_time:
            raise forms.ValidationError("End time must be after start time")

        return cleaned_data

    def clean_image_urls(self):
        image_urls = self.cleaned_data.get('image_urls')
        if image_urls == "":
            return []
        return image_urls

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