from django.forms import ModelForm
from modules.main.models import Merchandise

class MerchandiseForm(ModelForm):
    class Meta:
        model = Merchandise
        fields = ["image_url", "name", "description", "price"]