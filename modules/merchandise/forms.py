from django import forms
from django.forms import ModelForm
from modules.main.models import Merchandise

class MerchandiseForm(ModelForm):
    class Meta:
        model = Merchandise
        fields = ["image_url", "name", "description", "price"]
        
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price <= 0:
            raise forms.ValidationError("Price cannot be negative or zero")
        return price