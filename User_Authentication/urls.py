from django.urls import path
from . import views
app_name = 'user_side'

urlpatterns = [
  
  path("",views.index,name='index-page'),
  path("login", views.userlogin, name="userlogin"),
  path("signup", views.signup, name="signup"),
  path("logout",views.user_logout,name="userlogout"),
  path("verify_otp",views.verify_otp,name="verify_otp"),
  path("sent_otp",views.sent_otp,name="sent_otp"),
  path("resend_otp",views.resend_otp,name="resend_otp"),
  
  
  path('product_page',views.product_page, name='product_page'),
  path('product_page/<slug:category_slug>/', views.product_page, name='filtered_products_by_category'),
  path('product_page/price/<str:price_range>/', views.product_page, name='filtered_products_by_price'),
  path('product_page/sort/<str:sort_by>/', views.product_page, name='sort_product'),
  path('product_detail/<int:product_id>/', views.product_detail, name='product_detail'),
  
  
  path('user_profile',views.user_profile,name='user_profile'),
  path('edit_profile',views.edit_profile,name='edit_profile'),
  
  
  path('address',views.address_page,name='address_page'),
  path('add_address/', views.add_address, name='add_address'),
  path('edit_address/<int:address_id>/', views.edit_address, name='edit_address'),
  path('delete_address/<int:address_id>/', views.delete_address, name='delete_address'),
  path('set_default_address/<int:address_id>/', views.set_default_address, name='set_default_address'), 
   
  
  path('change_password',views.change_password,name='change_password'),
  path('send_otp',views.change_password_send_otp,name='change_password_send_otp'),
  path('otp_verification',views.change_password_verify_otp,name='change_password_verify_otp'),
  
  
  path('checkout/', views.checkout, name='checkout'),
  path('place_order/', views.place_order, name='place_order'),
  path('order_history/', views.order_history, name='order_history'),
  path('ordered_product_details/<int:order_id>', views.ordered_product_details, name='ordered_product_details'),
  path('download_invoice/<int:order_id>/', views.download_invoice, name='download_invoice'),
  
  
  path('return_order/<int:order_id>/', views.return_order, name='return_order'),
  
  
  path('pay_with_cash_on_delivery/<int:order_id>/', views.pay_with_cash_on_delivery, name='pay_with_cash_on_delivery'),
]
