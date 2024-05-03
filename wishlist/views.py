from django.shortcuts import render
from django.shortcuts import render,redirect
from django.contrib.auth.decorators import login_required
from User_Authentication.models import *
from category.views import *
from cart.models import *
from .models import *
from django.utils import timezone
from django.contrib import messages
from django.http import HttpResponseRedirect



@login_required(login_url='user_side:userlogin')
def add_to_wishlist(request,product_id):
    product=Product.objects.get(product_id=product_id)
    if WishList.objects.filter(user=request.user, product=product).exists():
        messages.success(request, 'Item is already in your wishlist.')
    else:
        # If it's not in the wishlist, create a new WishlistItem
        WishList.objects.create(user=request.user, product=product)
        messages.success(request, 'Item added to your wishlist.')

    return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_page'))



@login_required(login_url='user_side:userlogin')
def add_to_wishlist_product_detail(request, product_id):
    print("inside the add_to_wishlist_product_detail *********************************************************")
    size = request.GET.get('size')
    product = Product.objects.get(product_id=product_id)
    
    try:
        variant = ProductVariant.objects.get(product=product, size=size)
    except ProductVariant.DoesNotExist:
        variant = None
    
    if variant is not None:
        if request.user.is_authenticated:
            if WishList.objects.filter(user=request.user, product=product, variant=variant).exists():
                messages.success(request, 'Item is already in your wishlist.')
            else:
                WishList.objects.create(user=request.user, product=product, variant=variant)
                messages.success(request, 'Item added to your wishlist.')
        else:
            messages.error(request, 'Please log in to add items to your wishlist.')
    else:
        messages.error(request, 'Selected variant is not available.')

    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    
  

@login_required(login_url='user_side:userlogin')
def display_wishlist(request):
    wishlist_items = WishList.objects.filter(user=request.user)
    user_wishlist_products = [item.product for item in wishlist_items]
    context = {
        'wishlist_items': wishlist_items,
        'user_wishlist_products': user_wishlist_products,
    }
    return render(request, 'user-side/wishlist_page.html', context)

  
  
@login_required(login_url='user_side:userlogin')
def remove_wishlist(request,product_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    # Check if the item is in the user's wishlist
    try:
        wishlist_item = WishList.objects.get(user=request.user, product=product)
        wishlist_item.delete()  # Remove the item from the wishlist
        messages.success(request, 'Item removed from your wishlist.')
    except WishList.DoesNotExist:
        messages.error(request, 'Item is not in your wishlist.')
    
    return redirect(request.META.get('HTTP_REFERER', 'wishlist:wishlist_page'))

@login_required(login_url='user_side:userlogin')
def add_item_from_wishlist(request,product_id):
    product=get_object_or_404(Product, product_id=product_id)
    wishlist_item = WishList.objects.get(user=request.user, product=product)
    wishlist_item.delete()
    return redirect('user_side:product_detail',product_id=product_id)