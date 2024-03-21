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

# Create your views here.
@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def view_coupon(request):
    if not request.user.is_authenticated:
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
def add_coupon(request):
    if not request.user.is_authenticated:
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
def coupon_status(request,id):
    if not request.user.is_authenticated:
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
def edit_coupon(request,id):
    
    if not request.user.is_authenticated:
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