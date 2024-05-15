from django.shortcuts import render,redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseRedirect
from cart.models import *
from category.models import *
from coupon.models import *
from User_Authentication.models import *
import json
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.mail import EmailMessage
from django.contrib import messages
import razorpay

from django.shortcuts import render, redirect
from django.contrib import messages
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.http import HttpResponse
from User_Authentication.models import Order, Payment, OrderProduct
from cart.models import CartItem
from coupon.models import Coupon

@login_required(login_url='user_side:userlogin')
def payments(request):
    id = request.GET.get('order_id')
    payment_id = request.GET.get('payment_id')
    payment_method = request.GET.get('method')
    payment_order_id = request.GET.get('payment_order_id')
    status = request.GET.get('status')
    applied_coupon = request.session.get('coupon_code')
    coupon_discount = 0

    if applied_coupon:
        coupon = Coupon.objects.get(coupon_code=applied_coupon)
        coupon_discount = coupon.coupon_discount
        del request.session['coupon_code']

    try:
        order = Order.objects.get(user=request.user, is_ordered=False, order_number=id)
        payment = Payment(
            user=request.user,
            payment_id=payment_id,
            payment_method=payment_method,
            amount_paid=order.order_total,
            status=status,
            discount=coupon_discount,
            
        )
        payment.save()

        order.payment = payment
        order.is_ordered = True
        order.save()
    except Order.DoesNotExist:
        return HttpResponse("Order not found or already processed.")

    # Store transaction details inside Payment model
    # Move the cart items to orderproduct table
    cart_items = CartItem.objects.filter(user=request.user)
    for item in cart_items:
        item.variations.stock -= item.quantity
        item.variations.save()
        orderproduct = OrderProduct()
        orderproduct.order = order
        orderproduct.payment = payment
        orderproduct.user = request.user
        orderproduct.product = item.product
        orderproduct.quantity = item.quantity
        orderproduct.product_price = item.product.price
        orderproduct.size = item.variations.size
        orderproduct.ordered = True
        
        orderproduct.save()

    # Clear cart
    cart_items.delete()

    # Send order received email to customer
    mail_subject = 'Thank you for your order!'
    message = render_to_string('user-side/order_received_email.html', {
        'user': request.user,
        'order': order,
        'order_date': order.created_at,  # Include order date
        'delivery_address': order.full_address(),  # Include delivery address
        'ordered_products': OrderProduct.objects.filter(order=order),  # Include order summary
        'total_price': order.order_total,  # Include total price
        'payment_method': payment.payment_method,  # Include payment method
    })
    to_email = request.user.email
    email = EmailMessage(mail_subject, message, to=[to_email])
    email.send()

    context = {
        'order': order,
        'ordered_products': OrderProduct.objects.filter(order=order),
        'order_number': order.order_number,
        'transID': payment.payment_id,
        'subtotal': order.order_total,
        'payment': payment,
        'coupon_discount': coupon_discount,
    }

    return render(request, 'user-side/order_confirmed.html', context)
