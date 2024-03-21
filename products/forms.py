from django import forms
from .models import ProductImage
from products.models import Product, ProductVariant, SIZE_CHOICES

class AddProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['product_name', 'category', 'brand', 'description', 'price', 'image']
        

class AddVariantForm(forms.ModelForm):
    size = forms.ChoiceField(choices=SIZE_CHOICES, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = ProductVariant
        fields = ['product', 'size', 'stock', 'is_active']
        

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']
