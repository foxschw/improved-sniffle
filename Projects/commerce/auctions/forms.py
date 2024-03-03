from django import forms
from .models import Listings, Categories

class CreateListingForm(forms.ModelForm):
    # Defining fields for which I want human-friendly labels, 
    # change default widget type, or use a foreign key.
    item = forms.CharField(label="Item Name", max_length=64)
    price = forms.DecimalField(label="Starting Bid", decimal_places=2, max_digits=8)
    image = forms.URLField(label="Image URL", max_length=500)
    description = forms.CharField(widget=forms.Textarea, max_length=500)
    category = forms.ModelChoiceField(
        queryset=Categories.objects.all(), 
        empty_label="Category", 
        to_field_name="name"
    )
    
    class Meta:
        model = Listings
        fields = ["item", "description", "price", "image", "category"]