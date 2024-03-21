from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.core.mail import send_mail
from functools import wraps
from django.views.decorators.csrf import csrf_protect
from django.urls import reverse
from User_Authentication.models import *
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import HttpResponseBadRequest


# Create your views here.
#####################SUPER ADMIN REQUIRED####################
def superadmin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superadmin:
            return view_func(request, *args, **kwargs)
        else:
            messages.error(request, "Invalid admin credentials!")
            return redirect('admin_side:adminlogin')
    return _wrapped_view

####################ADMIN LOGIN####################

@csrf_protect
def adminlogin(request):
    if request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:dashboard')

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        
        print(email, password)
        user = authenticate(request, email=email, password=password)
        print("user",user)
        if user:
            if user.is_superadmin:
                login(request, user)
                messages.success(request, "Admin login successful!")
                return redirect('admin_side:dashboard')
            messages.error(request, "Invalid admin credentials!")


    return render(request, 'admin-side/adminlogin.html')

####################DASHBOARD####################

@login_required(login_url='admin_side:adminlogin')  
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def dashboard(request):
    return render(request, 'admin-side/admindashboard.html')
  
####################ADMIN LOGOUT####################  

def adminlogout(request):
    logout(request)
    return redirect('admin_side:adminlogin')
  

####################USER LIST####################

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def userlist(request):
    
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    search_query = request.GET.get('search', '')

    # Query the users based on the search query
    if search_query:
        users = Account.objects.filter(username__icontains=search_query)
    else:
        users = Account.objects.all().order_by('-date_joined')

    context = {
        'users': users
    }

    return render(request, 'admin-side/userlist.html', context)

####################USER BLOCK/UNBLOCK########################  

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def block_unblock_user(request, user_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    user = get_object_or_404(Account, id=user_id)

    # Toggle the is_blocked status of the user
    if user.is_active:
        user.is_active=False
        if request.user == user:
            logout(request)

    else:
        user.is_active=True
        
    user.save()
        

    return redirect('admin_side:userlist')


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def order_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    orders = Order.objects.all().order_by('-created_at')
    context = {'orders':orders}
    return render(request,'admin-side/orderlist.html',context)


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def ordered_product_details(request,order_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    order = Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)
    
    total = 0
    
    for ordered_product in ordered_products:
        total += ordered_product.product_price
        
    context = {
        'order':order,
        'ordered_products':ordered_products,
        'total': total,
    }
    return render(request,'admin-side/ordered_product_details.html',context)


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def update_order_status(request,order_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=int(order_id))
        status = request.POST['status']
        order.status = status
        order.save()
        return redirect('admin_side:order_list')
    else:
        return HttpResponseBadRequest("Bad request.")