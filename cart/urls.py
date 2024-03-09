from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    path('shopping_cart/', views.cart, name='shopping_cart'),
    path('add_cart/<int:product_id>/', views.add_cart, name='add_cart'),
    path('add_quantity_to_cart/<int:product_id>/<int:cart_item_id>/', views.add_quantity_to_cart, name='add_quantity_to_cart'),
    path('remove_cart/<int:product_id>/<int:cart_item_id>/', views.remove_cart, name='remove_cart'),
    path('remove_cart_item/<int:product_id>/<int:cart_item_id>/', views.remove_cart_item, name='remove_cart_item'),
    
    
    
    path('ajax/update/cart/', views.newcart_update, name='newcart_update'),
    path('ajax/remove/cart/', views.remove_cart_item_fully, name='remove_cart_item_fully'),
    
]
