from django.urls import path
from . import views

app_name = 'admin_side'


urlpatterns = [
    path('',views.adminlogin,name="adminlogin"),
    path('dashboard',views.dashboard,name="dashboard"),
    path('adminlogout',views.adminlogout,name="adminlogout"),
    path('userlist',views.userlist,name="userlist"),
    path('block_unblock_user/<int:user_id>/', views.block_unblock_user, name='block_unblock_user'),
]
