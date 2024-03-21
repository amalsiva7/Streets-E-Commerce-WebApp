from django.shortcuts import render,HttpResponse,redirect
from .forms import *
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
from products.models import *
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.db.models import Q


# Create your views here.

########################################BRAND########################################

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def brand_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    search_query = request.GET.get('search')

    if search_query:
        brands = Brand.objects.filter(Q(brand_name__icontains=search_query))
    else:
        brands = Brand.objects.all()

    return render(request, 'admin-side/brandlist.html', {'brands': brands})



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_brand(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':
        brand_name = request.POST.get('brand_name')
        if brand_name:  # Check if brand_name is not empty
            brand = Brand.objects.create(brand_name=brand_name)
            return redirect('product_side:brandlist')
        else:
            # If brand_name is empty, display an error message or handle it as needed
            # For example, you can add a message to the context and render the form again
            context = {'error_message': 'Brand name cannot be empty'}
            return render(request, 'admin-side/addbrand.html', context)
    
    return render(request, 'admin-side/addbrand.html')




@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_brand(request,brand_name):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    brands = get_object_or_404(Brand, brand_name=brand_name)
    if request.method=='POST':
        brand_name = request.POST.get('brand_name')
        brands.brand_name = brand_name
        brands.save()
        return redirect('product_side:brandlist')

    else:
        context = {
            'brands':brands
        }

    return render(request, 'admin-side/editbrand.html', context)  


@login_required(login_url='admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_brand(request, brand_name):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    brand = get_object_or_404(Brand, brand_name=brand_name)
    if request.method == 'POST':
        brand.delete()
        return redirect('product_side:brandlist')
    return redirect('product_side:brandlist')

########################################PRODUCT########################################

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def product_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    search_query = request.GET.get('search','')
    
    if search_query:
        products = Product.objects.filter(product_name__icontains = search_query,is_active=True)
    else:
        products = Product.objects.filter(is_active = True)
    
    return render(request,'admin-side/productlist.html',{'products': products})

  
@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_product(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')

    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        product_name = request.POST.get('product_name')
        category_id = request.POST.get('category')
        description = request.POST.get('description')
        price = request.POST.get('price')
        brand_id = request.POST.get('brand')
        images = request.FILES.getlist('images[]')
        stock = request.POST.get('stock')
        
        # Perform validation checks
        if not all([product_id, product_name, category_id, description, price, brand_id, images, stock]):
            messages.error(request, "Please fill in all the fields.")
            return redirect('product_side:add_product')
        
        try:
            brand = Brand.objects.get(id=brand_id)
            category = Category.objects.get(pk=category_id)

            # Attempt to create a new product
            product = Product(product_name=product_name, product_id=product_id, description=description, 
                              category=category, price=price, brand=brand)
            product.image = images[0]
            product.save()
            
            # Save additional product images
            for img in images:
                prd_image = ProductImage(product=product, image=img)
                prd_image.save()
            
            messages.success(request, 'Product added successfully.')
            return redirect('product_side:productlist')
        
        except Exception as e:
            messages.error(request, str(e))
            return redirect('product_side:add_product')

    else:
        form = AddProductForm()
        
    context = {
        'form': form,
        'categories': categories,
        'brand': brands,
    }
    return render(request,'admin-side/addproduct.html',context)



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def edit_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    categories = Category.objects.all()
    brands = Brand.objects.all()
    
    # Retrieve the product to be edited
    try:
        product = Product.objects.get(pk=product_id)
    except Product.DoesNotExist:
        # Handle the case where the product doesn't exist
        return HttpResponse("Product not found", status=404)

    if request.method == 'POST':
        # Update the product with the form data
        product.product_name = request.POST.get('product_name')
        product.category = Category.objects.get(pk=request.POST.get('category'))
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.brand = Brand.objects.get(pk=request.POST.get('brand'))
        product.stock = request.POST.get('stock')

        # Handle image updates (if needed)
        new_images = request.FILES.getlist('images[]')
        if new_images:
            
            # Clear existing product images and add new ones
            ProductImage.objects.filter(product=product).delete()
            for image in new_images:
                prd_image = ProductImage(product=product, image=image)
                prd_image.save()

        # Save the updated product
        product.save()

        return redirect('product_side:productlist')
    else:
        # Populate the form with existing product data
        form = AddProductForm(instance=product)

    context = {
        'form': form,
        'categories': categories,
        'brands': brands,
        'product': product,  # Include the product object in the context for reference
    }  
    return render(request, 'admin-side/editproduct.html', context)


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def soft_delete_product(request, product_id):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')

    try:
        product = Product.objects.get(product_id=product_id)
        product.is_active = False  # Mark the product as inactive (soft deleted)
        product.save()
        messages.success(request, f"Product '{product.product_name}' has been soft deleted.")
    except Product.DoesNotExist:
        messages.error(request, "Product not found.")
   
    return redirect('product_side:productlist')


# @login_required(login_url='admin_side:adminlogin')
# @cache_control(no_cache=True, must_revalidate=True, no_store=True)
# def undo_delete(request):
#     if not request.user.is_authenticated:
#         return redirect('admin_side:adminlogin')


########################################PRODUCT VARIANTS########################################
@login_required(login_url='account:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def variant_list(request):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    search_query = request.GET.get('search', '')
    
    if search_query:
        product_variant = ProductVariant.objects.filter(
            Q(size__icontains = search_query)|
            Q(stock__icontains = search_query)|
            Q(product__product_name__icontains=search_query)
        )
    else:
        product_variant = ProductVariant.objects.all().order_by('-created_date')
        #it'll fetch all the data in created order
        
    context = {'product_variant':product_variant}
    return render(request,'admin-side/variantlist.html',context)


@login_required(login_url='account:admin_login')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def add_variant(request,variant_id=None):
    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    if variant_id:
        variant = get_object_or_404(ProductVariant,id=variant_id)
    else:
        variant=None
        
    if request.method == 'POST':
        if variant:
            form = AddVariantForm(request.POST,instance=variant)
        else:
            form = AddVariantForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('product_side:variant-list')
        
    else:
        if variant:
            form = AddVariantForm(instance=variant)
        else:
            form = AddVariantForm()
            
    context= {
        'form' : form,
        'variant_id' : variant_id
    }
    
    return render(request,'admin-side/addvariant.html',context)

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def delete_variant(request, variant_id):

    if not request.user.is_authenticated:
        return redirect('admin_side:adminlogin')
    
    variant = get_object_or_404(ProductVariant, id=variant_id)
    
    # Set is_active to False
    variant.is_active = False
    variant.save()
    
    return redirect('product_side:variant-list')

