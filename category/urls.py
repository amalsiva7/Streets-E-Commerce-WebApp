from django.urls import path
from . import views

app_name = 'category_side'

urlpatterns = [
    path('categorylist',views.category_list,name='categorylist'),
    path('add-category',views.add_category,name='add-category'),
    path('delete-category/<str:category_name>/',views.delete_category,name='delete-category'),
    
]