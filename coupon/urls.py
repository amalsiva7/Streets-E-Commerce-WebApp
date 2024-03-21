from django.urls import path
from . import views
app_name = 'coupon'

urlpatterns = [
    path('view_coupon/',views.view_coupon,name='view_coupon'),
    path('add_coupon/',views.add_coupon,name='add_coupon'),
    path('generate_coupon/',views.generate_coupon,name='generate_coupon'),
    path('coupon_status/<int:id>', views.coupon_status, name='coupon_status'),
    path('edit_coupon/<int:id>/', views.edit_coupon, name='edit_coupon'),
    
    
    
]
