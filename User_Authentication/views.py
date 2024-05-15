from django.shortcuts import render,HttpResponse,redirect,get_object_or_404, reverse
from django.core.exceptions import ObjectDoesNotExist
from django.contrib import messages
from django.contrib.auth.models import User
from django.views.decorators.cache import cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate,login,logout
from django.contrib.sessions.models import Session
from django.core.mail import send_mail
import random
import datetime
from random import sample
from django.db.models import Q
from .models import *
from products.models import *
from cart.models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import AddressBook
from .forms import AddressForm
from wishlist.models import *
from coupon.models import *
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import razorpay
from django.db.models import Case, When, Value, IntegerField
from django.db.models import F, FloatField
from django.db.models.functions import Cast,Abs


# Create your views here.

from django.db.models import Count

def index(request):    
    
    search_query = request.GET.get('search_product')
    cart_items_count = 0
    wishlist_items_count = 0
    
    # Fetch all products from the database
    all_products = Product.objects.filter(is_active=True)
    
    # Get 4 random products from the list of all products
    try:
        random_products = sample(list(all_products), 4)
    except:
        random_products = []
    
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(user=request.user, is_active=True).count()
        wishlist_items_count = WishList.objects.filter(user=request.user).count()
        
    print(cart_items_count,wishlist_items_count,"Cart Count Wishlist Count*************************************")
    
    # Pass the random products and counts to the template context
    context = {
        'products': random_products,
        'cart_count': cart_items_count,
        'wishlist_count': wishlist_items_count
    }
    
    # Render the template with the context
    return render(request, 'user-side/index.html', context)



####################  LOGIN  ###################

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def userlogin(request):
    
    # Redirect if user is already authenticated
    if request.user.is_authenticated:
        return redirect('user_side:index-page')

    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print(email, password)
        
        try:
            
            if Account.objects.filter(email=email).exists():
                existing_account = Account.objects.get(email=email)
                
                if not existing_account.is_emailverified:
                    messages.error(request, "Invalid Email Address")
                    return redirect('user_side:userlogin')
            
            if not Account.objects.filter(email=email, is_active=True).exists():
                messages.error(request, "Your account is inactive or blocked")
                return redirect('user_side:userlogin')
            
            user = authenticate(request, email=email, password=password)
           
            
            if user is None:
                messages.error(request, "Invalid Credentials")
                return redirect('user_side:userlogin')
            else:
                login(request,user)
                
                return redirect('user_side:index-page')
        
        except Exception as e:
            # Handle any other exceptions that might occur during login
            print(f"An error occurred during login: {e}")
            messages.error(request, "An error occurred during login. Please try again later.")
            return redirect('user_side:login')
        
    return render(request, "user-side/login-user.html")


#############################  USER LOGOUT #############################

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "logout successful!")
    return redirect('user_side:index-page')

#############################  USER SIGNIN #############################

from django.shortcuts import render

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def signup(request):
    if request.user.is_authenticated:
        return redirect('user_side:index-page')

    if request.method == 'POST':
        user_name = request.POST.get('user')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('pass1')
        confirm_password = request.POST.get('pass2')

        if not user_name or not email or not phone or not password or not confirm_password:
            messages.warning(request, "All fields are required")
            return redirect("user_side:signup")

        try:
            if Account.objects.filter(email=email).exists():
                existing_account = Account.objects.get(email=email)
                if existing_account.is_emailverified:
                    messages.error(request, "Email Address already exists")
                    return redirect("user_side:userlogin")
                else:
                    existing_account.delete()

            if password != confirm_password:
                messages.warning(request, "Passwords do not match")
                return redirect("user_side:signup")

            if len(password) < 8:
                messages.warning(request, "Password must be at least 8 characters long")
                return redirect("user_side:signup")

            if not any(char.islower() for char in password):
                messages.warning(request, "Password must contain at least one lowercase letter")
                return redirect("user_side:signup")

            if not any(char.isupper() for char in password):
                messages.warning(request, "Password must contain at least one uppercase letter")
                return redirect("user_side:signup")

            if not any(char.isdigit() for char in password):
                messages.warning(request, "Password must contain at least one digit")
                return redirect("user_side:signup")

            if not any(char in '@$!%*?&' for char in password):
                messages.warning(request, "Password must contain at least one special character")
                return redirect("user_side:signup")

        except Exception as e:
            # Handle the exception (e.g., print error message, log, etc.)
            print(f"An error occurred: {e}")
            messages.error(request, "An error occurred while processing your request")
            return redirect("user_side:signup")
        
        
        referral_id = str(uuid.uuid4())[:8]

        # If no exception occurs, create the user
        myuser = Account.objects.create_user(user_name, email, phone, password,referral_id=referral_id)
        
        print(myuser.referral_id,"**********************************************************************************************")

        request.session['user_name'] = user_name
        request.session['email'] = email

        return redirect("user_side:sent_otp")
    
    return render(request, "user-side/signup-user.html")


def sent_otp(request):
    random_num = random.randint(10000, 99999)
    request.session['OTP_Key'] = random_num
    email = request.session.get('email')  # Retrieve email from session
    user_name = request.session.get('user_name')  # Retrieve user name from session
    
    # Check if email is already set in the session
    if not email:
        # If email is not set, retrieve it from the request POST data and set it in the session
        email = request.POST.get('email')
        request.session['email'] = email
        request.session['user_name'] = user_name  # Store user name in session as well
    
    send_mail(
        "OTP Verification for Your Street$ Account",
        f"Dear {user_name},\n\nThank you for choosing to sign up with Street$! To ensure the security of your account, we require a one-time password (OTP) verification.\n\nPlease use the following OTP to complete your account registration:\n\n{random_num} - OTP\n\nRegards,\nThe Street$ Team",
        "amalsiva7210@gmail.com",
        [email],
        fail_silently=False,
    )
    
    # Redirect to OTP verification page
    return redirect('user_side:verify_otp')


def verify_otp(request):
   user=Account.objects.get(email=request.session['email'])
   if request.method=="POST":
      if str(request.session['OTP_Key']) != str(request.POST['otp']):
         print(request.session['OTP_Key'],request.POST['otp'] ,"***********************************************************************************************")
         user.is_emailverified=False
         user.save()
         messages.error(request, "Wrong OTP")
         
      else:
         user.is_emailverified=True
         user.save()
         login(request,user)
         messages.success(request, "signup successful!")
         
         
         
         return redirect('user_side:index-page')
   return render(request,'user-side/verify_otp.html')


def resend_otp(request):
    if request.user.is_authenticated:
        return redirect('user_side:index-page')
    
    random_num = random.randint(10000, 99999)
    request.session['OTP_Key'] = random_num
    email = request.session.get('email')  # Retrieve email from session
    user_name = request.session.get('user_name')  # Retrieve user name from session
    
    # Check if email is already set in the session
    if not email:
        # If email is not set, retrieve it from the request POST data and set it in the session
        email = request.POST.get('email')
        request.session['email'] = email
        request.session['user_name'] = user_name  # Store user name in session as well
    
    send_mail(
        "OTP Verification for Your Street$ Account",
        f"Dear {user_name},\n\nThank you for choosing to sign up with Street$! To ensure the security of your account, we require a one-time password (OTP) verification.\n\nPlease use the following OTP to complete your account registration:\n\n{random_num} - OTP\n\nRegards,\nThe Street$ Team",
        "amalsiva7210@gmail.com",
        [email],
        fail_silently=False,
    )
    
    # Redirect to OTP verification page
    return redirect('user_side:verify_otp')
    

################################ PRODUCT PAGE ################################

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def product_page(request):
    category_slug = request.GET.get('category_slug')
    price_range = request.GET.get('price_range')
    sort_by = request.GET.get('sort_by')
    search_query = request.GET.get('search_product')
    cart_items_count = 0
    wishlist_items_count = 0
    
    print(category_slug,"*********************************************CATEGORY SLUG IN PRODUCT PAGE*********************************************")

    products = Product.objects.filter(is_active=True,productvariant__isnull=False).distinct() 
    
    for p in products:
        print(p.rprice,"***************************************************************RPRICE IN PRODUCT_PAGE****************************")

    if category_slug:
        # Filter products based on category
        products = products.filter(category__slug=category_slug)

    if price_range:
        # Filter products based on price range
        min_price, max_price = map(float, price_range.split('-'))
        products = products.filter(price__gte=min_price, price__lte=max_price)

    if search_query:
        # Filter products based on search query
        products = products.filter(Q(product_name__icontains=search_query) | Q(description__icontains=search_query))

    if sort_by == 'low_to_high':
        products = products.order_by('price')
    elif sort_by == 'high_to_low':
        products = products.order_by('-price')
    elif sort_by == 'new_arrivals':
        products = products.order_by('-product_id')
    elif sort_by == 'aA_to_zZ':
        if price_range:
            # Sort products within the specified price range alphabetically by product name (aA to zZ)
            products = products.filter(price__gte=min_price, price__lte=max_price).order_by('product_name')
        else:
            # Sort all products alphabetically by product name (aA to zZ)
            products = products.order_by('product_name')
    elif sort_by == 'zZ_to_aA':
        if price_range:
            # Sort products within the specified price range alphabetically by product name (zZ to aA)
            products = products.filter(price__gte=min_price, price__lte=max_price).order_by('-product_name')
        else:
            # Sort all products alphabetically by product name (zZ to aA)
            products = products.order_by('-product_name')
            
    if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(user=request.user, is_active=True).count()
        wishlist_items_count = WishList.objects.filter(user=request.user).count()
        
    products = products.annotate(deducted_price=Cast(Abs(F('rprice') - F('price')), FloatField()))
    # offer_discount = Offer.objects.filter('discount')
        

    context = {
        'products': products,
        'category_slug': category_slug,
        'price_range': price_range,
        'sort_by': sort_by,
        'cart_items_count':cart_items_count,
        'wishlist_items_count':wishlist_items_count,
        # 'offer_discount':offer_discount
    }
    return render(request, 'user-side/product.html', context)


###############################################################################PRODUCT FILTERING###############################################################################
def shop_product_list(request):

    products = Product.objects.filter(is_active=True)
    selected_brands = []
    selected_categories = []

    # Filter products based on brand and category
    brand_list = request.GET.getlist("brand")
    category_list = request.GET.getlist("category")
    min_price = request.GET.get("min_price")
    max_price = request.GET.get("max_price")

    if brand_list:
        products = products.filter(product_brand__in=brand_list, is_active=True)
        for product in products:
            selected_brands.append(product.product_brand.id)

    if category_list:
        products = products.filter(product_category__in=category_list, is_active=True)
        for product in products:
            selected_categories.append(product.product_category.id)
    
    if min_price and max_price:
        products = products.filter(offer_price__range=[min_price, max_price], is_active=True)


    # Paginate the filtered products
    paginator = Paginator(products, 9)
    page = request.GET.get("page", 1)

    try:
        paginated_products = paginator.page(page)
    except PageNotAnInteger:
        paginated_products = paginator.page(1)
    except EmptyPage:
        paginated_products = paginator.page(paginator.num_pages)

    # Pass the paginated products, categories, and brands to the template
    content = {
        "products": paginated_products,
        "categories": Category.objects.filter(is_available=True),
        "brands": Brand.objects.filter(status=True),
        "selected_brands": selected_brands,
        "selected_categories": selected_categories,
    }

    return render(request, "user_side/shop-product-list.html", content)
###############################################################################PRODUCT FILTERING###############################################################################


def stock_check(request):
    variant = request.POST.get('variant')
    product_id = request.POST.get('product')
    
    product_variant = get_object_or_404(ProductVariant, product_id=product_id, size=variant)
    product = get_object_or_404(Product, pk=product_id)
    
    context = {
        'product_id': product_id,
        'product_name': product.product_name,
        'price': product.price,
        'description': product.description,
        'selected_size': variant,
        'stock': product_variant.stock
    }
    
    return JsonResponse(context)

   


@cache_control(no_cache=True, no_store=True, must_revalidate=True)
def product_detail(request, product_id):
    
    variant = request.POST.get('variant')
    product = request.POST.get('product')
    
    stocks = None
    try:
        products_data = ProductVariant.objects.get(product_id=product, size=variant)
        
        stocks = products_data.stock
    except:
        pass
   
    products = get_object_or_404(Product, pk=product_id)
    product_variants = ProductVariant.objects.filter(product=product_id)
    selected_size = request.GET.get('size')  # Get the selected size from the query parameters
    if selected_size:
        product_variants = product_variants.filter(size=selected_size)
        
    print("product detail page is selected stock *******************:", stocks)
    context = {
        'products': products,# product details
        'product_variants': product_variants, # varients
        'selected_size': selected_size, # size
        'stock':stocks
    }
    print("++++++++++++++++++++")
    print(context)
    if request.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest':
        # If the request is AJAX, return a JSON response with the context data
        print("if rerequest.headers.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest' in  product detail page '(If the request is AJAX, return a JSON response with the context data)'")
        return JsonResponse({'success': True, 'context': context})
    else:
        print("If the request is AJAX, return a JSON response with the context data in product detail page")
        # If the request is not AJAX, render the template as usual
        return render(request, 'user-side/blu.html', context)
    


################################ USER PROFILE  ################################

@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def user_profile(request):
    if not request.user.is_authenticated:
        return render(request,'user-side/index.html')
    
    user_profile = Account.objects.get(email=request.user.email)

    context = {
        'user_profile': user_profile,
    }
    return render(request,'user-side/user-profile.html',context)


@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required
def edit_profile(request):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')
    
    user_profile = Account.objects.get(email=request.user.email) # Get the UserProfile instance for the logged-in user

    if request.method == 'POST':
        # Handle the form submission and update the user details
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        # email = request.POST.get('email')
        mobile = request.POST.get('mobile')

        # Update the user profile fields with the form data
        user_profile.first_name = first_name
        user_profile.last_name = last_name
        user_profile.username = username
        # user_profile.email = email
        user_profile.phone_number = mobile

        # Save the changes to the UserProfile and User models
        user_profile.save()

        return redirect('user_side:user_profile')  # Redirect to the user profile page after successful update
    else:
        return render(request, 'user-side/edit_profile.html', {'user_profile': user_profile})




@cache_control(no_cache=True, no_store=True, must_revalidate=True)
# @login_required(login_url='user_side:userlogin')
def forgot_password(request):
    if request.method != "POST":
        print("inside the not post ion forgot password **************************************************** ")
        return render(request, "user-side/forgot_password.html")
    else:
        pass1 = request.POST["re_password"]
        pass2 = request.POST["password"]
        email=request.POST["email"]
        if pass1 != pass2:
            messages.warning(request, "password not correct")
            return redirect("user-side/forgot_password.html")
        
        try:
            user = Account.objects.get(email=email)
        except ObjectDoesNotExist:
            messages.warning(request, "your user email not available, plese enter a valid email")
        request.session['email']=email
        request.session['password']=pass1
        return redirect('user_side:sent-otp-forgot-password')
    
  
def sent_otp_forgot_password(request):
    # Generate a random 4-digit OTP
    random_num = random.randint(1000, 9999)
    # Store the OTP in the session
    request.session['OTP_Key'] = random_num
    
    # Fetch the user's name and email from the session
    user_name = request.session.get('user_name')
    # Compose the email message
    email_subject = "Password Reset OTP"
    email_body = f"""Dear {user_name},

You've requested to reset your password for your [Website/App Name] account. Please use the following One-Time Password (OTP) to complete the process:

OTP: {random_num}

This OTP is valid for 60 seconds. Please do not share it with anyone for security reasons.

If you did not initiate this request, please ignore this message.

Thank you,
[Your Company/Website Name] Team -OTP"""

    # Send the email
    send_mail(
        email_subject,
        email_body,
        "amalsiva7210@gmail.com",
        [request.session['email']],
        fail_silently=False,
    )
    
    # Redirect to the OTP verification page
    return redirect('user_side:verify-otp-forgot-password')


def verify_otp_forgot_password(request):
   user=Account.objects.get(email=request.session['email'])
   if request.method=="POST":
      if str(request.session['OTP_Key']) != str(request.POST['otp']):
         print(request.session['OTP_Key'],request.POST['otp'])
        #  user.is_active=True
      else:
         password=request.session['password']
         user.set_password(password)
         user.save()
         login(request,user)
         messages.success(request, "password changed successfully!")
         return redirect('user_side:userlogin')
   return render(request,'user-side/verify_otp.html')



@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required(login_url='user_side:userlogin')
def change_password(request):
    if request.method != "POST":
        request.session['email']=request.user.email
        return render(request, "user-side/change_password.html")
    else:
        pass1 = request.POST["re_password"]
        pass2 = request.POST["password"]
        if pass1 != pass2:
            messages.warning(request, "password not correct")
            return redirect("user_side:change_password")
        request.session['password']=pass1
        return redirect('user_side:change_password_send_otp')


@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required(login_url='user_side:userlogin')
def change_password_send_otp(request):
    random_num = random.randint(1000, 9999)
    request.session['OTP_key'] = random_num

    user = Account.objects.get(email=request.session['email'])
    username = user.username

    send_mail(
        "OTP Verification for Changing PasswordYour Street$ Account",
        f"Dear {username},\n\nThank you for choosing to sign up with Street$! To ensure the security of your account, we require a one-time password (OTP) verification.\n\nPlease use the following OTP to complete your account registration:\n\n{random_num} - OTP\n\nRegards,\nThe Street$ Team",
        "amalsiva7210@gmail.com",
        [user.email],
        fail_silently=False,
    )
    return redirect('user_side:change_password_verify_otp')


@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required(login_url='user_side:userlogin')
def change_password_verify_otp(request):
    user = Account.objects.get(email=request.session['email'])
    
    if request.method == 'POST':
        
        if str(request.session['OTP_key']) != str(request.POST['otp']):
            messages.error(request, "OTP verification failed")
            return redirect('user_side:user_profile')
        else:
            password = request.session['password']
            user.set_password(password)
            user.save()
            messages.success(request,"Password changed successfully.")
            logout(request)
            return redirect('user_side:userlogin')
    return render(request,'user-side/verify_otp.html')
             
      

################################ ADDRESSS MANIPULATION  ################################


@login_required(login_url='user_side:userlogin')
def address_page(request):
    if not request.user.is_authenticated:
        return redirect('user_side:userlogin')
    
    user = request.user
    addresses = AddressBook.objects.filter(user=user)
    default_address = addresses.filter(is_default=True).first()
    
    print(addresses,default_address,"****************************************************************************")

    context = {
        'addresses': addresses,
        'default_address': default_address
    }
    return render(request, 'user-side/address-page.html', context)



@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required(login_url='user_side:userlogin')
def add_address(request):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')

    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        phone = request.POST.get('phone').strip()
        email = request.POST.get('email').strip()
        address_line_1 = request.POST.get('address_line_1').strip()
        address_line_2 = request.POST.get('address_line_2').strip()
        country = request.POST.get('country').strip()
        state = request.POST.get('state').strip()
        city = request.POST.get('city').strip()
        pincode = request.POST.get('pincode').strip()

        # Validate all fields to ensure they are not empty (spaces are considered empty)
        if not (first_name and last_name and phone and email and address_line_1 and country and state and city and pincode):
            return render(request, 'user-side/add_address.html', {'error_message': 'All fields are required'})

        # Create a new shipping address instance
        address = AddressBook(user=request.user, first_name=first_name, last_name=last_name, phone=phone,
                              email=email, address_line_1=address_line_1, address_line_2=address_line_2,
                              country=country, state=state, city=city, pincode=pincode)
        address.save()

        # Set is_default attribute of the newly added address and reset previous default
        AddressBook.objects.filter(user=request.user, is_default=True).update(is_default=False)
        address.is_default = True
        address.save()

        return redirect('user_side:address_page')

    else:
        return render(request, 'user-side/add_address.html')




@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required(login_url='user_side:userlogin')
def edit_address(request, address_id):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')

    address = get_object_or_404(AddressBook, id=address_id, user=request.user)

    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            # Clean the data to remove leading/trailing spaces
            cleaned_data = form.cleaned_data
            for key, value in cleaned_data.items():
                if isinstance(value, str):
                    cleaned_data[key] = value.strip()
            form.cleaned_data = cleaned_data

            if not all(cleaned_data.values()):
                # If any field is empty after stripping, render the form with an error message
                return render(request, 'user-side/edit_address.html', {'form': form, 'error_message': 'All fields are required'})

            form.save()
            return redirect('user_side:address_page')
    else:
        form = AddressForm(instance=address)

    return render(request, 'user-side/edit_address.html', {'form': form})



@cache_control(no_cache=True, no_store=True, must_revalidate=True)
@login_required(login_url='user_side:userlogin')
def delete_address(request, address_id):
    address = get_object_or_404(AddressBook, id=address_id)

    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Address deleted successfully.')
        return redirect(reverse('user_side:address_page'))

    return redirect(reverse('user_side:userlogin'))


@login_required(login_url='user_side:userlogin')
def checkout(request, total=0, quantity=0, cart_items=None):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')
    try:
        tax = 0
        grand_total = 0
        coupon_discount = 0

        if request.user.is_authenticated:
            cart_items = CartItem.objects.filter(user=request.user, is_active=True)
            
        else:
            pass

        for cart_item in cart_items:
            total += (cart_item.product.price * cart_item.quantity)
            quantity += cart_item.quantity

            try:
                variant = cart_item.variations
                if variant.stock <= 0:
                    # variant.stock -= cart_item.quantity
                    # variant.save()
                    print("Not enough stock!")
            except ObjectDoesNotExist:
                pass

        tax = (2 * total) / 100
            

        grand_total = total + tax  # Apply coupon discount to grand_total

        
    except ObjectDoesNotExist:
        pass

    address_list = AddressBook.objects.filter(user=request.user)
    default_address = address_list.filter(is_default=True).first()
    context = {
        'total': total,
        'quantity': quantity,
        'cart_items': cart_items,
        'tax': tax,
        'grand_total': grand_total,
        'address_list': address_list,
        'default_address': default_address,  # Pass the default address to the context
        
    }
    return render(request, 'user-side/checkout.html', context)


@login_required(login_url='user_side:userlogin')
def set_default_address(request, address_id):
    if not request.user.is_authenticated:
        return redirect('user_side:userlogin')
    
    addr_list = AddressBook.objects.filter(user=request.user)
    for a in addr_list:
        a.is_default = False
        a.save()
    address = AddressBook.objects.get(id=address_id)
    address.is_default=True
    address.save()
    return redirect('user_side:checkout')


from django.conf import settings
from coupon.views import apply_coupon
@login_required(login_url='user_side:userlogin')
def place_order(request, total=0, quantity=0):
    if not request.user.is_authenticated:
        return redirect('user_side:userlogin')
    
    current_user = request.user

    #If the cart count is less than 0, then redirect back to home
    cart_items = CartItem.objects.filter(user=current_user)
    cart_count = cart_items.count()
    if cart_count <= 0:
        return redirect('user_side:index-page')
    

    grand_total = 0
    tax = 0
    coupon_discount = 0
    
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100

    grand_total = total + tax 
    

    if request.method == 'POST':
        
        try:
            address = AddressBook.objects.get(user=request.user,is_default=True)
        except:
            messages.warning(request, 'No delivery address exists! Add a address and try again')
            return place_order(request)
        
        
        data = Order()
        data.user = current_user
        data.first_name = address.first_name
        data.last_name = address.last_name
        data.phone = address.phone
        data.email = address.email
        data.address_line_1 = address.address_line_1
        data.address_line_2 = address.address_line_2
        data.city = address.city
        data.state = address.state
        data.country = address.country
        data.pincode = address.pincode
        data.order_total = grand_total
        data.tax = tax
        data.ip = request.META.get('REMOTE_ADDR')
        data.save()

        #Generate order number
        yr = int(datetime.date.today().strftime('%Y'))
        dt = int(datetime.date.today().strftime('%d'))
        mt = int(datetime.date.today().strftime('%m'))
        d = datetime.date(yr,mt,dt)
        current_date = d.strftime("%Y%m%d")
        order_number = current_date + str(data.id)
        data.order_number = order_number
        data.save()

        order = Order.objects.get(user=current_user, is_ordered=False, order_number=order_number)
        
        coupons = Coupon.objects.all()
        
        client = razorpay.Client(auth=(settings.RAZOR_PAY_KEY_ID, settings.RAZOR_PAY_SECRET_KEY))
        
        delivery_charges = 54
        
        
        context = {
            'order': order,
            'cart_items': cart_items,
            'total': total,
            'tax': tax,
            'grand_total': grand_total+delivery_charges,
            'coupons': coupons,
            'coupon_discount':coupon_discount,
            'delivery_charges':delivery_charges,
        }

        if grand_total > 1000:
            messages.error(request, "Cash on delivery is not available for orders exceeding 1000. Please choose another payment method.")
            return render(request, 'user-side/payment.html', context)
        else:
            return render(request, 'user-side/payment.html', context)
    else:
        return redirect('user_side:checkout')
   
   
    
@login_required(login_url='user_side:userlogin')  
def pay_with_cash_on_delivery(request, order_id):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')
    
    cur_user = request.user
    order = Order.objects.get(id=order_id)
    print('***************order*************',order)
     
    if order.order_total >= 1000:
        messages.error(request, "COD is acceptable for payment above 1000. Please choose other options")
        return redirect('user_side:place_order')
     
    payment_id = f'uw{order.order_number}{order_id}'
    payment = Payment.objects.create(
        user=cur_user, 
        payment_method='Cash on Delivery',
        payment_id=payment_id,
        amount_paid=order.order_total,
        status='COMPLETED')
    
    payment.save()
    order.is_ordered = True
    order.payment = payment
    order.save()

    cart_items = CartItem.objects.filter(user=request.user)

    for item in cart_items:
        if item.variations.stock >= item.quantity:  # Check if there is sufficient stock
            orderproduct = OrderProduct()
            item.variations.stock -= item.quantity
            item.variations.save()
            orderproduct.order_id = order.id
            orderproduct.payment = payment
            orderproduct.user_id = request.user.id
            orderproduct.product_id = item.product_id
            orderproduct.quantity = item.quantity
            orderproduct.product_price = item.product.price
            orderproduct.ordered = True
            orderproduct.size = item.variations.size
            orderproduct.save()
        else:
            # If stock is insufficient, display message and remove item from cart
            messages.error(request, f"Oops! Item '{item.product.product_name}' is sold out.")
            item.delete()
            


    # Clear the cart (adjust this based on your project structure)
    cart_items.delete()

    tax = 0
    total = 0
    quantity = 0
    for cart_item in cart_items:
        total += (cart_item.product.price * cart_item.quantity)
        quantity += cart_item.quantity
    tax = (2 * total)/100
    grand_total = total + tax
    print('******grand total*****', grand_total)

    ordered_products = OrderProduct.objects.filter(order_id=order_id)
    subtotal = 0
    for i in ordered_products:
            subtotal += i.product_price * i.quantity

    print('*****subtotal*****',subtotal)         

    context = {
        'order': order,
        'ordered_products': ordered_products,
        'order_number': order.order_number,
        'transID': payment.payment_id,
        'cart_items': cart_items,
        'total': total,
        'tax': tax,
        'grand_total': grand_total,
        'subtotal': subtotal,
        'payment': payment,
        }

    # Redirect to the order confirmed page
    return render(request, 'user-side/order_confirmed.html', context)

@login_required(login_url='user_side:userlogin')
def order_history(request):
    if not request.user.is_authenticated:
        return redirect('user_side:user_login')

    # Assuming Order.objects.all() returns all orders
    all_orders = Order.objects.filter(user=request.user, is_ordered=True).order_by('-created_at')

    # Number of orders to display per page
    per_page = 3

    paginator = Paginator(all_orders, per_page)
    
    page_number = request.GET.get('page')
    try:
        orders = paginator.page(page_number)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        orders = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        orders = paginator.page(paginator.num_pages)

    context = {
        'orders': orders,
        'all_orders':all_orders
    }
    return render(request, 'user-side/order_history.html', context)



@login_required(login_url='user_side:userlogin')
def ordered_product_details(request, order_id):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')
    
    order = Order.objects.get(id=order_id)
    ordered_products = OrderProduct.objects.filter(order=order)
    context = {
        'order': order,
        'ordered_products': ordered_products,
    }
    return render(request, 'user-side/ordered_product_details.html', context)



@login_required(login_url='user_side:userlogin')
def download_invoice(request, order_id):
    if not request.user.is_authenticated:
        return redirect('user_side:index-page')
    
    order_number = request.GET.get('order_number')
    transID = request.GET.get('payment_id')
   

    try:
        order = Order.objects.get(id=order_id, is_ordered=True)
        ordered_products = OrderProduct.objects.filter(order_id=order.id)

        subtotal = 0
        for i in ordered_products:
            subtotal += i.product_price * i.quantity

        payment = Payment.objects.get(id=order.payment.id)

       


        context = {
            'order': order,
            'ordered_products': ordered_products,
            'order_number': order.order_number,
            'transID': payment.payment_id,
            'subtotal': subtotal,

        }
        return render(request, 'user-side/order_confirmed.html', context)
    
    except (Payment.DoesNotExist, Order.DoesNotExist):
        return redirect('user_side:index-page')
    
    

@login_required(login_url='user_side:userlogin')
def return_order(request, order_id):
    order = Order.objects.get(id=order_id)
    order_method=order.payment.payment_method
    if  order_method!='Cash on Delivery'and order.status == 'Delivered':
        user_profile = request.user
       
        # Update the order status to 'Returned'
        order.status = 'Returned'
        order.save()
        for order_product in order.orderproduct_set.all():
            if order_product.variations.exists():
                for variation in order_product.variations.all():
                    variation.stock += order_product.quantity
                    variation.save()
        messages.warning(request, 'return request has been send. amount sucessfully returned to your wallet')

    elif order_method=='Cash on Delivery' and order.status == 'Delivered':
        order.status = 'Returned'
        order.save()
        messages.warning(request, 'return request has been send.')

    elif order_method=='Cash on Delivery' and order.status != 'Delivered' :
        order.status = 'Cancelled'
        order.save()
        messages.warning(request, 'return request has been send.')
    else:
        user_profile = request.user

        order.status = 'Cancelled'
        order.save()
        for order_product in order.orderproduct_set.all():
            if order_product.variations.exists():
                for variation in order_product.variations.all():
                    variation.stock += order_product.quantity
                    variation.save()
        messages.warning(request, 'cancel request has been send.')

    
    
        
    return redirect('user_side:order_history') 