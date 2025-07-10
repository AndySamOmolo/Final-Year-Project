from django import forms
from bakery.models import BakeryItem, Category

class BakeryItemForm(forms.ModelForm):
    class Meta:
        model = BakeryItem
        fields = ['name', 'description', 'price', 'image', 'available', 'category', 'ingredients']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
            'ingredients': forms.Textarea(attrs={'rows': 4, 'cols': 50}),
        }
