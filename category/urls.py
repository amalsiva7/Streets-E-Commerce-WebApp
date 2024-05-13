from django.urls import path
from . import views

app_name = 'category_side'

urlpatterns = [
    path('categorylist',views.category_list,name='categorylist'),
    path('add-category',views.add_category,name='add-category'),
    path('delete-category/<str:category_name>/',views.delete_category,name='delete-category'),
    path('edit-category/<str:category_name>/',views.edit_category,name='edit-category'),
    
    
    
    
    path('category_offer/', views.category_offer, name='category_offer'),
    path('edit_offer/<int:offer_id>/', views.edit_offer, name='edit_offer'),
    path('delete_offer/<int:offer_id>/', views.delete_offer, name='delete_offer'),
]