from django.shortcuts import render,redirect
from .models import *
from django.contrib.auth.decorators import login_required 
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import cache_control
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, F, Value, Count
from datetime import datetime, timedelta
from collections import defaultdict
from Admin_panel.views import *

# Create your views here.

########################################CATEGORY########################################

@login_required(login_url='admin_side:adminlogin')
@superadmin_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_list(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    search_query = request.GET.get('search')

    if search_query:
        categories = Category.objects.filter(Q(category_name__icontains=search_query))
    else:
        categories = Category.objects.all()

    context={
        'categories':categories
    } 

    return render(request,'admin-side/categorylist.html',context)


@login_required(login_url='admin_side:adminlogin')
@superadmin_required
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_category(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':
        category_name = request.POST.get('category_name')

        if category_name:  # Check if category_name is not empty
            category = Category(category_name=category_name)
            category.save()
            messages.success(request, 'Category added successfully.')
            return redirect('category_side:categorylist')
        else:
            messages.error(request, 'Category name cannot be empty.')
            return redirect('category_side:add-category')  # Redirect back to the form page

    return render(request, 'admin-side/addcategory.html')

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def edit_category(request,category_name):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    category=get_object_or_404(Category, category_name=category_name)
    if request.method=='POST':
        category_name=request.POST['category_name']
        category.category_name = category_name
        category.save()

        return redirect('category_side:categorylist')
    else:
        context = {
            'category':category
        }
    
    return render(request, 'admin-side/edit_category.html', context)
    
    


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def delete_category(request,category_name):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    category = get_object_or_404(Category, category_name = category_name)
    
    if request.method == 'POST':
        category.delete()
        return redirect('category_side:categorylist')
    
    return redirect('category_side:categorylist')


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def category_offer(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':

        category_id = request.POST.get('category')
        discount = float(request.POST.get('discount'))
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')

        category = Category.objects.get(id=category_id)
        if Offer.objects.filter(category=category).exists():
            messages.warning(request, "There is Already One Discount offer on this product")
            return redirect('category_side:category_offer')
        # if len(str(discount)) <= 2 or discount == 100:
        print(category_id, discount, start_date, end_date)
        discount = int(discount) / 100
        category = Category.objects.get(id=category_id)
        dis = Offer(discount=(discount * 100), category=category, start_date=start_date, end_date=end_date)
        dis.save()
        product_list = Product.objects.filter(category=category)
        
        print(product_list,"*******************************************PRODUCT LIST IN CATEGORY OFFER********************************************")
        
        for product in product_list:
            discount_percent = dis.discount
            price_float = float(product.price)
            discount_percent_float = float(discount_percent)
            discount_amount = (price_float *discount_percent_float) / 100
            product.rprice = discount_amount
            product.save()
            
            
        messages.success(request, f'{discount*100}% Discount Added for all Products under {category.category_name}')
        return redirect('category_side:category_offer')



        # offer = Offer.objects.create(category=category, discount_percentage=discount_percentage, start_date=start_date, end_date=end_date)
        # offer.save()

        # Redirect to the same page to show the updated offers
        return redirect('category_side:category_offer')

    categories = Category.objects.all()
    added_offers = Offer.objects.all()

    context = {'categories': categories, 'added_offers': added_offers,}
    return render(request, 'admin-side/category_offer.html', context)



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_offer(request, offer_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    offer = get_object_or_404(Offer, id=offer_id)

    if request.method == 'POST':
        # Process the form data to update the offer
        offer.discount = float(request.POST.get('discount_percentage'))
        offer.start_date = request.POST.get('start_date')
        offer.end_date = request.POST.get('end_date')
        offer.save()
        
        product_list = Product.objects.filter(category=offer.category)
        
        
        
        for product in product_list:
            discount_percent = offer.discount
            price_float = float(product.price)
            discount_percent_float = float(discount_percent)
            discount_amount = (price_float *discount_percent_float) / 100
            product.rprice = discount_amount
            product.save()
            print(product.rprice,"*******************************************PRODUCT LIST RPRICE IN CATEGORY OFFER********************************************")
        
        
        return redirect('category_side:category_offer')
    
    categories = Category.objects.all()

    context = {
        'offer': offer,
        'categories':categories,
               }
    return render(request, 'admin-side/edit_offer.html', context)



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_offer(request, offer_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    offer = get_object_or_404(Offer, id=offer_id)

    if request.method == 'POST':
        product_list = Product.objects.filter(category=offer.category)
        for product in product_list:
            product.rprice=0.00
            product.save()
        offer.delete()
        return redirect('category_side:category_offer') 

    return redirect('category_side:category_offer')