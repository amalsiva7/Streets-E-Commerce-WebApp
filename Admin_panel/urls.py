from django.urls import path
from . import views

app_name = 'admin_side'


urlpatterns = [
    path('',views.adminlogin,name="adminlogin"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('adminlogout',views.adminlogout,name="adminlogout"),
    path('userlist',views.userlist,name="userlist"),
    path('block_unblock_user/<int:user_id>/', views.block_unblock_user, name='block_unblock_user'),
    
    
    path('order_list/', views.order_list, name='order_list'),
    path('ordered_product_details/<int:order_id>',views.ordered_product_details,name='ordered_product_details'),
    path('update_order_status/<int:order_id>',views.update_order_status,name='update_order_status')
]
