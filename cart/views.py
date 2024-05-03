from django.shortcuts import render,redirect,HttpResponseRedirect,get_object_or_404
from django.http import JsonResponse, HttpResponseBadRequest
from category.models import *
from .models import *
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.urls import reverse

# Create your views here.

def _cart_id(request):
    cart = request.session.session_key
    if not cart:
        cart = request.session.create()
    return cart


def cart(request, total=0, quantity=0, cart_items=None):
    try:
        tax=0
        grand_total=0
        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
        else:
            cart = Cart.objects.get(cart_id = _cart_id(request))
            cart_items = CartItem.objects.filter(cart=cart, is_active=True)
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total)/100
        grand_total = total+tax
    except ObjectDoesNotExist:
        pass 

    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total
    }

    return render(request, 'user-side/shoping-cart.html', context)



def add_cart(request, product_id): 
    size = request.GET.get('size')
    product = Product.objects.get(product_id=product_id)
    
    try:
        variant = ProductVariant.objects.get(product=product, size=size)
    except ProductVariant.DoesNotExist:
        messages.warning(request, 'variation not available, please select another variation')
        return HttpResponseRedirect(reverse('user_side:product_detail', args=(product_id,)))
        
    if variant is not None:  # Check if variant was found
        if variant.stock >= 1:
            if request.user.is_authenticated:
                try:
                    is_cart_item_exists = CartItem.objects.filter(
                        user=request.user, product=product,
                        variations=variant).exists()
        
                except CartItem.DoesNotExist:
                    pass 
                  
                if is_cart_item_exists:
                    
                    to_cart = CartItem.objects.get(user=request.user, product=product, variations=variant)
                    variation = to_cart.variations
                    if to_cart.quantity < variation.stock:
                        to_cart.quantity += 1
                        to_cart.save()
                    else:
                        messages.success(request, "product out of stock")
                else:
                    cart = Cart.objects.create(cart_id=_cart_id(request))
                    to_cart = CartItem.objects.create(
                        user=request.user,
                        product=product,
                        variations=variant,  # Set the selected variation here
                        quantity=1,  # Set the initial quantity
                        is_active=True)
                    # to_cart.variations.set([variant])  
                return redirect('cart:shopping_cart')
            else:

                messages.success(request, "please login to purchase")
                return redirect('user_side:userlogin')
        else:
          
            messages.warning(request, 'This item is out of stock.')
            return redirect('user_side:product_detail', product_id)
    else:
        messages.warning(request, 'Variant not found.')  # Add an error message for debugging
        return redirect('user_side:product_detail', product_id)
    


def add_quantity_to_cart(request, product_id, cart_item_id):
    product = get_object_or_404(Product, product_id=product_id)
    
    try:
        # Get the specific cart item by ID
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart_item = CartItem.objects.get(product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
        
        # Check if there are any variations associated with the product
        if product.variation_set.exists():
            # You may want to choose a specific variation to increment quantity
            # In this example, I'll just increment the quantity of the first variation
            first_variation = product.variation_set.first()
            if first_variation.stock >= 1 and cart_item.quantity < first_variation.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                print("Not enough stock for the selected variation")
        else:
            # Handle products without variations here
            if cart_item.quantity < product.stock:
                cart_item.quantity += 1
                cart_item.save()
            else:
                print("Not enough stock for the product")
    
    except CartItem.DoesNotExist:
        pass  # Handle the case where the cart item doesn't exist

    # Redirect back to the shopping cart page
    return HttpResponseRedirect(reverse('cart:shopping_cart'))



def remove_cart_item(request, product_id, cart_item_id):
    product = get_object_or_404(Product, product_id=product_id)

    try:
        if request.user.is_authenticated:
            # If the user is authenticated, remove the cart item associated with the user
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            # If the user is not authenticated, remove the cart item associated with the session cart
            cart_item = CartItem.objects.get(product=product, cart__cart_id=_cart_id(request), id=cart_item_id)
        
        # Delete the cart item
        cart_item.delete()
    except CartItem.DoesNotExist:
        pass  # Handle the case where the cart item doesn't exist

    # Redirect back to the shopping cart page
    return redirect('cart:shopping_cart')


def remove_cart(request, product_id, cart_item_id):
    
    product = get_object_or_404(Product, product_id=product_id)

    try:
        if request.user.is_authenticated:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
        else:
            cart = Cart.objects.get(cart_id=_cart_id(request))
            cart_item = CartItem.objects.get(product=product, cart=cart, id=cart_item_id)
        if cart_item.quantity > 1:
            variant = cart_item.variations
            variant.stock += 1
            cart_item.quantity -= 1

            variant.save()
            cart_item.save()    
        else:
            cart_item.delete()
    except:
        pass
    return redirect('cart:shopping_cart')




def newcart_update(request):
    new_quantity = 0
    total = 0
    tax = 0
    grand_total = 0
    quantity=0
    counter=0

    if request.method == 'POST' and request.user.is_authenticated:
        prod_id = int(request.POST.get('product_id'))
        cart_item_id = int(request.POST.get('cart_id'))
        qty=int(request.POST.get('qty'))
        counter=int(request.POST.get('counter'))
        print(qty)
        product = get_object_or_404(Product, product_id=prod_id)

        try:
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)
        except CartItem.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Cart item not found'})
        
        if cart_item.variations:
            print(cart_item.variations)
            variation = cart_item.variations  # Access the variation associated with the cart item
            if cart_item.quantity < variation.stock:
                cart_item.quantity += 1
                cart_item.save()
                # total = cart_item.quantity * product.price
                # tax = (2 * total) / 100
                # grand_total = total + tax
                sub_total=cart_item.quantity * product.price
                new_quantity = cart_item.quantity
            else:
                message = "out of stock"
                return JsonResponse({'status': 'error', 'message': message}) 
        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity
        tax = (2 * total) / 100
        grand_total = total + tax
        print(new_quantity,total,tax,grand_total,sub_total)       
        # Handle variations as needed
        
    if new_quantity ==0:
        message = "out of stock"
        return JsonResponse({'status': 'error', 'message': message})
    else:
        return JsonResponse({
            'status': "success",
            'new_quantity': new_quantity,
            "total": total,
            "tax": tax,
            'counter':counter,
            "grand_total": grand_total,
            "sub_total":sub_total,
            
        })
        



def remove_cart_item_fully(request):
    if request.method == 'POST' and request.user.is_authenticated:
        try:
            counter = int(request.POST.get('counter'))
            product_id = int(request.POST.get('product_id'))
            cart_item_id = int(request.POST.get('cart_id'))

            # Get the product and cart item
            product = get_object_or_404(Product, product_id=product_id)
            cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
            cart_items = CartItem.objects.filter(user=request.user)

            # Check if the cart item exists and belongs to the logged-in user
            if cart_item.quantity > 1:
                cart_item.quantity -= 1
                cart_item.save()
                sub_total = cart_item.quantity * product.price

                total = 0
                quantity = 0

                for cart_item in cart_items:
                    total += (cart_item.product.price * cart_item.quantity)
                    quantity += cart_item.quantity

                tax = (2 * total) / 100
                grand_total = total + tax
                current_quantity = cart_item.quantity

                return JsonResponse({
                    'status': 'success',
                    'tax': tax,
                    'total': total,
                    'grand_total': grand_total,
                    'counter': counter,
                    'new_quantity': current_quantity,
                    'sub_total': sub_total,  # Updated quantity
                })
            else:
                cart_item = CartItem.objects.get(product=product, user=request.user, id=cart_item_id)
                cart_item.delete()
                message = "the cart iem has bee deleted"
                return JsonResponse({'status': 'error', 'message': message}) 

        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

    return HttpResponseBadRequest('Invalid request')