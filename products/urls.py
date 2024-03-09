from django.urls import path
from . import views

app_name = 'product_side'

urlpatterns = [
    path('productlist',views.product_list,name='productlist'),
    path('add_product',views.add_product,name='add_product'),
    path('editproduct/<str:product_id>',views.edit_product,name='editproduct'),
    path('deleteproduct/<str:product_id>',views.soft_delete_product,name='soft_delete_product'),
    
    
    path('variantlist',views.variant_list,name='variant-list'),
    path('addvariant',views.add_variant,name='add-variant'),
    path('add-variant/<str:variant_id>', views.add_variant, name='edit-variant'),
    path('delete_variant/<int:variant_id>', views.delete_variant, name='delete-variant'),
    
    
    path('add_brand',views.add_brand,name='add_brand'),
    path('brandlist',views.brand_list,name='brandlist'),
    path('edit_brand/<str:brand_name>',views.edit_brand,name='edit_brand'),
    path('delete_brand/<str:brand_name>',views.delete_brand,name='delete_brand'),
]
