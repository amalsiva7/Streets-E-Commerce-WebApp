from django.urls import path
from . import views
app_name = 'wallet'

urlpatterns = [
    path('payment/<order_id>/',views.payment,name='payment'),
    
    
    path('wallet/', views.wallet, name='wallet'),
    path('wallet_payment/<int:order_id>/', views.wallet_payment, name='wallet_payment'),
    path('order_return/<int:order_id>/', views.order_return, name='order_return'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
    
]
