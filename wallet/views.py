from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import *
from coupon.models import *
from User_Authentication.models import *
from category.views import *
from cart.models import *
from django.utils import timezone
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


# Create your views here.

@login_required(login_url='user_side:userlogin')
def payment(request, order_id):
    coupon_discount = 0
    # try:
    order = Order.objects.get(id=order_id)
    # Check if the coupon is valid for the cart total
        # Redirect back to the cart with the updated total and applied coupon
    current_user = request.user
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('user_side:index-page')
        

    grand_total = 0
    tax = 0
    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax

    try:

        applied_coupon = request.session['coupon_code']

        if applied_coupon:
            coupon = Coupon.objects.get(coupon_code=applied_coupon)
            print('*********coupon***********',coupon)
            coupon_discount = coupon.discount_amount
            print('**********coupon_discount**********', coupon_discount)

        context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': order.order_total,
        'coupon_discount':coupon_discount
    }    
    except :
        context = {
        'order': order,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': order.order_total,
        'coupon_discount':coupon_discount
    }
    
    
    return render(request, 'user-side/payment.html', context)
  

def wallet_balance(request, user_id):
    datas = Transaction.objects.filter(user=user_id)
    grand_total = 0
    for data in datas:
        if data.transaction_type == "Credit":
            grand_total += data.amount
        else:
            grand_total -= data.amount
    return grand_total

  
@login_required(login_url='user_side:userlogin')
def wallet(request):
    user_id = request.user
    print(user_id,"****************************************************************************")
    user_id = Account.objects.get(email=user_id)
    
    total = wallet_balance(request,user_id.id)
    transactions = Transaction.objects.filter(user=user_id).order_by("id").reverse()
    
    
    paginator = Paginator(transactions, 6)  # Show 10 transactions per page
    page = request.GET.get('page')
    
    try:
        transaction_history = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        transaction_history = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        transaction_history = paginator.page(paginator.num_pages)

    content = {
        "transaction_history":transaction_history,
        "wallet_total": total,
    }

    return render(request, "user-side/wallet.html",content)
  


@login_required(login_url='user_side:userlogin')
def wallet_payment(request, order_id,coupon_code=None):
      
    id = request.user
    order_main = Order.objects.get(id=order_id)
    
    print("Order_id :",order_id,"   Order_main total: ",order_main.order_total, "checking the values in wallet_payment function")

    user = Account.objects.get(email=id)
    wallet_amount = wallet_balance(request, id)
    
    # Check if order_product exists before accessing its attributes
    if order_main.order_total > wallet_amount:
        print("Inside the Wallet payment function if wallet amount is less than order amount *********************************************")
        messages.warning(request, "Insufficient Balance!")
        return redirect("user_side:checkout")

    order_main.payment_status = True
    order_main.save()

    if coupon_code is not None and coupon_code != "None":
        coupon = Coupon.objects.get(coupon_code=coupon_code)
        user = Account.objects.get(id=request.user.id)
        User_Coupon.objects.create(
            user=user,
            coupon_code=coupon.Coupon_code,
            coupon_discount=coupon.discount,
            order_id=order_main           
        )

    cart_ids = CartItem.objects.filter(user=id).values_list('cart', flat=True).distinct()
    Transaction.objects.create(
        user=user,
        description="Placed Order  " + str(order_main.order_number),  #Convert order_id to string
        amount=order_main.order_total,
        transaction_type="Debit",
    )
    
    # Clearing the cart after payment
    data = Cart.objects.filter(id__in=cart_ids)  # Filtering carts based on retrieved IDs
    data.delete()


    return render(request, "user-side/order_confirmed.html", {"order_id": order_id})
  


@login_required(login_url='user_side:userlogin')
def cancel_order(request, order_id):
    user_id = request.user.id
    print(order_id,"************************* CANCEL ORDER****************************")
    
    data = Order.objects.get(id=order_id)
    data.status = "Cancelled"
    data.save()
    
    payment = data.payment
    payment_id = payment.payment_id
    if (
        payment.payment_method == "RAZORPAY"
        or payment.payment_method == "Wallet"
    ):
        amount = data.order_total
        user = Account.objects.get(id=user_id)

        Transaction.objects.create(
            user=user,
            description="Cancelled Order " + str(data.order_number),
            amount=amount,
            transaction_type="Credit",
        )
    
    for order_product in data.orderproduct_set.all():
        if order_product.variations.exists():
            for variation in order_product.variations.all():
                variation.stock += order_product.quantity
                variation.save()

    data.save()

    return redirect("user_side:order_history")


@login_required(login_url='user_side:userlogin')
def order_return(request, order_id):
    user_id = request.user.id
    print(order_id, "************************* RETURN ORDER ****************************")
   
    data = Order.objects.get(id=order_id)
    data.status = "Returned"
    data.save()
    
    payment = data.payment
    payment_id = payment.payment_id
    if (
        payment.payment_method == "RAZORPAY"
        or payment.payment_method == "Wallet"
    ):
        amount = data.order_total
        user = Account.objects.get(id=user_id)

        Transaction.objects.create(
            user=user,
            description="Returned Order " + str(data.order_number),
            amount=amount,
            transaction_type="Credit",
        )
    
    for order_product in data.orderproduct_set.all():
        if order_product.variations.exists():
            for variation in order_product.variations.all():
                variation.stock += order_product.quantity
                variation.save()

    data.save()

    return redirect("user_side:order_history")



@login_required(login_url='user_side:userlogin')
def return_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        messages.error(request, 'Order does not exist.')
        return redirect('user_side:order_history')

    order_method = order.payment.payment_method
    order.order_total = order.payment.amount_paid
    
    print(order.order_total,"************************************ORDER TOTAL***********************************************")

    if order.status == 'Delivered':
        if order_method != 'Cash on Delivery':
            user_profile = request.user
            wallet, created = Wallet.objects.get_or_create(user=user_profile)
            
            # Credit the purchased amount back to the wallet
            wallet.amount += order.order_total
            wallet.save()
        # Update the order status to 'Returned' regardless of payment method
        if order_method == 'Cash on Delivery':
            order.status = 'Returned'
        else:
            order.status = 'Returned'
            messages.warning(request, 'Return request has been sent. Amount successfully returned to your wallet.')
    else:
        if order_method == 'Cash on Delivery':
            order.status = 'Cancelled'
            messages.warning(request, 'Return request has been sent.')
        else:
            user_profile = request.user
            wallet, created = Wallet.objects.get_or_create(user=user_profile)
            print(wallet)

            # Credit the purchased amount back to the wallet
            wallet.amount += order.order_total
            wallet.amount = round(wallet.amount, 2)
            wallet.save()

            order.status = 'Cancelled'
            messages.warning(request, 'Cancel request has been sent. Amount successfully returned to your wallet.')

    # If order has variations, increase stock for each ordered product variation
    for order_product in order.orderproduct_set.all():
        if order_product.variations.exists():
            for variation in order_product.variations.all():
                variation.stock += order_product.quantity
                variation.save()

    order.save()
    return redirect('user_side:order_history')