from django.urls import path,include
from . import views

app_name = 'payment'

urlpatterns = [

    path('payments/', views.payments, name='payments'),
    
]