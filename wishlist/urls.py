from django.urls import path
from . import views
app_name = 'wishlist'

urlpatterns = [
    path('wishlist/<product_id>/',views.add_to_wishlist,name='add_wishlist'),
    path('wishlist/product_detail/<product_id>/',views.add_to_wishlist_product_detail ,name='add_to_wishlist_product_detail'),
    path('display/wishlist',views.display_wishlist,name='wishlist_page'),
    path('wallet_coupon/remove/wishlist/<int:product_id>/', views.remove_wishlist, name='remove_wishlist'),
    
    
    path('add_from_wishlist/<int:product_id>',views.add_item_from_wishlist,name='add_from_wishlist'),
]
