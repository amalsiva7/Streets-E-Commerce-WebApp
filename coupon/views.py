from django.shortcuts import render
from User_Authentication.models import *
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_protect
from datetime import date,datetime
from coupon.models import *
import random
import string
from django.http import JsonResponse
from django.utils import timezone
from decimal import Decimal
from Admin_panel.views import *
from django.core.serializers import serialize

# Create your views here.
@login_required(login_url='admin_side:adminlogin')
@superadmin_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_coupon(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    current_date_time = datetime.now()
    current_date = current_date_time.date()
    
    coupons = Coupon.objects.filter(coupon_expiry=current_date)
    for coupon in coupons:
        coupon.is_active = False
        coupon.save()
    
    context={
        "coupons": Coupon.objects.all().order_by('-id'),
        "current_date":current_date
    }  
    
    return render(request,'admin-side/coupon.html',context)



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def add_coupon(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    today_date = date.today().isoformat()
    
    if request.method == "POST":
        min_amount = request.POST.get("minimumamount")
        discount_amt = request.POST.get("discount")
        expiry = request.POST.get("expirydate")
        coupon = request.POST.get("couponCode")
        status = True
        
        if datetime.strptime(expiry, '%Y-%m-%d').date() < date.today():
            status = False
        
        Coupon.objects.create(
            min_purchase = min_amount,
            coupon_discount = discount_amt,
            coupon_expiry = expiry,
            coupon_code = coupon,
            is_active = status
        )
        return redirect("coupon:view_coupon")
    
    return render(request,'admin-side/add_coupon.html')



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def generate_coupon(request):
    
    try:
        while True:
            raw_data = string.ascii_letters + string.digits
            random_coupon_name = ''.join(random.choice(raw_data) for _ in range(8))
            if not Coupon.objects.filter(coupon_code=random_coupon_name.upper()):
                return JsonResponse({"data": random_coupon_name.upper()})
    except Exception as e:
        print(e)
        return JsonResponse({"status": 400}, status=400)
  
    

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def coupon_status(request,id):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')

    coupon = Coupon.objects.get(id=id)
    if coupon.is_active:
        coupon.is_active = False
        coupon.save()
    else:
        coupon.is_active = True
        coupon.save()
    return redirect("coupon:view_coupon")




@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def edit_coupon(request,id):
    
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
        
    today_date = date.today().isoformat()
    
    if request.method == "POST":
        
        min_amount = request.POST.get("minimumamount")
        discount = request.POST.get("discount")
        expiry = request.POST.get("expirydate")
        coupon = request.POST.get("couponCode")
        
        
        coupon_data = Coupon.objects.get(id=id)
        coupon_data.min_purchase = min_amount
        coupon_data.coupon_discount = discount
        coupon_data.coupon_expiry = expiry
        coupon_data.coupon_code = coupon
        coupon_data.is_active = True
        coupon_data.save()
        print(coupon_data.min_purchase,coupon_data.coupon_discount,coupon_data.coupon_expiry,coupon_data.coupon_code,'*************************************************************')
        return HttpResponse(status=200)
    context = {
        "coupons": Coupon.objects.get(id=id),
        "date_today":today_date
    }
    return render(request,'admin-side/edit_coupon.html',context)
 

@login_required(login_url='user_side:userlogin')
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
def  apply_coupon(request):
    if request.method == 'POST':
        coupon_code = request.POST.get('coupon_code')
        order_id = request.POST.get('order_id')
        print(coupon_code,order_id,"*****************************************************************************")
        
        try:
            coupon = get_object_or_404(Coupon, coupon_code=coupon_code)
            order = Order.objects.get(id=order_id)
            
            print(coupon,order,"***************************************************")
            if coupon.coupon_expiry >= timezone.now().date() and coupon.is_active:
                if order.order_total >= coupon.min_purchase:
                    # Check if the coupon is already redeemed by the user
                    if coupon.is_redeemed_by_user(request.user):
                        
                        messages.error(request, 'Coupon has already been redeemed by you.')
                        
                        
                    else:
                        # Calculate discount amount based on percentage
                        discount_percentage = Decimal(coupon.coupon_discount)
                        discount_amount = (discount_percentage / Decimal(100)) * Decimal(order.order_total)
                        
                        print("-----------------------------------------",discount_amount)

                        # Apply the discount and calculate updated total
                        updated_total = Decimal(order.order_total) - discount_amount
                        order_tax_decimal = Decimal(order.tax)
                        grand_total = updated_total + order_tax_decimal
                        
                        order.order_total = updated_total
                        order.save()

                        # Mark the coupon as redeemed for the user
                        redeemed_details = User_Coupon.objects.create(user=request.user, coupon_code=coupon, is_redeemed=True)
                        redeemed_details_json = serialize('json', [redeemed_details])
                        
                        request.session['coupon_code'] = coupon_code
                        messages.success(request, 'Coupon applied successfully.')
                        # Redirect to payment page with updated order total
                        context = {
                            'tax': order.tax,
                            'total': order.order_total,
                            'discount_amount': discount_amount,
                            'coupon':float(coupon.coupon_discount),
                            'grand_total': grand_total,
                            'redeemed_details':redeemed_details_json
                        }
                        print(context, 'hello what is really') 
                        return JsonResponse(context)

                else:
                    messages.error(request, 'Coupon is not applicable for the order total.')
            else:
                
                messages.error(request, 'Coupon is not applicable for the current date.')
                

        except Coupon.DoesNotExist:
            
            messages.error(request, 'Invalid coupon code.')
    return JsonResponse({'data':'Invalid request'})
    # Redirect back to the payment page if coupon application fails
    # return redirect('wallet:payment', order_id)