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
def delete_category(request,category_name):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    category = get_object_or_404(Category, category_name = category_name)
    
    if request.method == 'POST':
        category.delete()
        return redirect('category_side:categorylist')
    
    return redirect('category_side:categorylist')

