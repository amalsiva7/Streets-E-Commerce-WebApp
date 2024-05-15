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
from products.models import *
from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from django.http import HttpResponseBadRequest
from datetime import datetime
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.template.loader import render_to_string
from xhtml2pdf import pisa
import pandas as pd
from io import StringIO 
from django.utils.timezone import make_aware
from django.db.models import F, ExpressionWrapper, DecimalField
from django.db.models import Sum
import calendar
from collections import defaultdict




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
    
    total_users_count = int(Account.objects.count())
    product_count = Product.objects.count()
    user_order = Order.objects.count()
    # for i in monthly_order_totals:
    completed_orders = Order.objects.filter()

    monthly_totals_dict = defaultdict(float)

    # Iterate over completed orders and calculate monthly totals
    for order in completed_orders:
        order_month = order.created_at.strftime('%m-%Y')
        monthly_totals_dict[order_month] += float(order.order_total)

    print(monthly_totals_dict)
    months = list(monthly_totals_dict.keys())
    totals = [round(value, 2) for value in monthly_totals_dict.values()]

    variants = ProductVariant.objects.filter(is_active=True)
    
    
    top_selling_products = OrderProduct.objects.values('product__product_name', 'product__product_id').annotate(num_of_sales=models.Count('product')).order_by('-num_of_sales')[:10]

    top_selling_categories = Category.objects.annotate(total_sales=Sum('product__orderproduct__quantity')).order_by('-total_sales')[:10]

    context = {
        'total_users_count': total_users_count,
        'product_count': product_count,
        'order': user_order,
        'variants': variants,
        'months': months,
        'totals': totals,
        'top_selling_products': top_selling_products,
        'top_selling_categories':top_selling_categories,
    }
    return render(request, 'admin-side/admindashboard.html',context)
  
####################ADMIN LOGOUT####################  
@superadmin_required
def adminlogout(request):
    logout(request)
    return redirect('admin_side:adminlogin')
  

####################USER LIST####################

@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def userlist(request):
    
    if not request.user.is_authenticated and request.user.is_superadmin:
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
@superadmin_required
def block_unblock_user(request, user_id):
    if not request.user.is_authenticated and request.user.is_superadmin:
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
@superadmin_required
def order_list(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    orders = Order.objects.all().order_by('-created_at')
    context = {'orders':orders}
    return render(request,'admin-side/orderlist.html',context)




@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def ordered_product_details(request,order_id):
    if not request.user.is_authenticated and request.user.is_superadmin:
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
@superadmin_required
def update_order_status(request,order_id):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':
        order = get_object_or_404(Order, id=int(order_id))
        status = request.POST['status']
        order.status = status
        order.save()
        return redirect('admin_side:order_list')
    else:
        return HttpResponseBadRequest("Bad request.")
    


    
@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def sales_report(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')

    order = OrderProduct.objects.all().order_by('id').reverse()
    order_count = order.count()
    total_order_product = order.aggregate(total=Sum(F('product_price') * F('quantity')))

    # If total_order_product is None (no records found), set it to 0
    total_order_product = total_order_product['total'] if total_order_product['total'] else 0
    
    total_order_product = round(total_order_product, 2)
    
    paginator = Paginator(order, 6)
    page = request.GET.get('page')
    
    try:
        objects = paginator.page(page)
    except PageNotAnInteger:
        objects = paginator.page(1)
    except EmptyPage:
        objects = paginator.page(paginator.num_pages)

    context = {
        "order":objects,
        "order_count":order_count,
        "total_order_product":total_order_product,
        "objects":objects
    }
    return render(request, "admin-side/sales_report.html",context )


@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def sales_report_search(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':
        try:
            query = request.POST.get('query')
            print("received query '(iinside sales-report-search)': ",query)
            order = OrderProduct.objects.filter(order__order_number=query)
            print(order,"sales-report-search********************************************************")
            if order.exists():
                context= {'order': order}
                return render(request, 'admin-side/sales_report.html',context )
            messages.warning(request, 'Not Found!')
        except Exception as e:
            print(e)
            messages.warning(request, f"An Error Occurred: {e}")
        
    return redirect('admin_side:sales-report')



@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def sales_date_search(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')
    
    if request.method == 'POST':
        try:
            start_date = request.POST.get('startDate')
            end_date = request.POST.get('endDate')
            
            print("Received start date:", start_date)
            print("Received end date:", end_date)
  
            if start_date and end_date:
                start_date = make_aware(datetime.strptime(start_date, '%Y-%m-%d'))
                end_date = make_aware(datetime.strptime(end_date, '%Y-%m-%d'))

                order = OrderProduct.objects.filter(created_at__range=(start_date, end_date))
                print(order,"sales date search, orderdata****************************************")
                if order.exists():
                    content = {
                        'order':order,
                        'start_date':start_date,
                        'end_date':end_date

                    }
                    return render(request, 'admin-side/sales_report.html',content)
                messages.warning(request,'Not Found!')
        except Exception as e:
            print(e)
            messages.warning(request, f"An Error Occured{e}")

    return redirect('admin_side:sales-report')




@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def sales_report_pdf(request):
    if not request.user.is_authenticated or not request.user.is_superadmin:
        return redirect('admin_side:adminlogin')

    try:
        start_date_str= request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
    except:
        pass
    
    order = None
   
    #If both start_date and end_date are provided, filter data accordingly
    if start_date_str and end_date_str:

        start_date = datetime.strptime(start_date_str, '%b. %d, %Y, midnight')
        end_date = datetime.strptime(end_date_str, '%b. %d, %Y, midnight')
       
        start_date_formatted = start_date.strftime('%Y-%m-%d')
        end_date_formatted = end_date.strftime('%Y-%m-%d')
        order = Order.objects.filter(date__range=[start_date_formatted, end_date_formatted])
    else:
       # If no dates provided, return all data
        order = Order.objects.all()

    context = {"order": order}
    html_content = render_to_string("admin-side/sales-report-pdf.html", context)
    pdf_response = HttpResponse(content_type="application/pdf")
    pdf_response["Content-Disposition"] = f'filename="{id}_details.pdf"'

    pisa_status = pisa.CreatePDF(html_content, dest=pdf_response)

    if pisa_status.err:
        return HttpResponse("error creating pdf")

    return pdf_response




@login_required(login_url='admin_side:adminlogin')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
@superadmin_required
def sales_report_excel(request):
    if not request.user.is_authenticated and request.user.is_superadmin:
        return redirect('admin_side:adminlogin')

    try:
        start_date_str= request.GET.get('start_date')
        end_date_str = request.GET.get('end_date')
    except:
        pass

    #If both start_date and end_date are provided, filter data accordingly
    if start_date_str and end_date_str:

        start_date = datetime.strptime(start_date_str, '%b. %d, %Y, midnight')
        end_date = datetime.strptime(end_date_str, '%b. %d, %Y, midnight')
       
        start_date_formatted = start_date.strftime('%Y-%m-%d')
        end_date_formatted = end_date.strftime('%Y-%m-%d')
        order = Order.objects.filter(date__range=[start_date_formatted, end_date_formatted])
    else:
       # If no dates provided, return all data
        order = Order.objects.all()

    context = {"order": order}
    # using the same template that is used for pdf generation
    html_content = render_to_string("admin-side/sales-report-pdf.html",context)
  
    df_list = pd.read_html(StringIO(html_content))
    df = df_list[0]  

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=sales-report.xlsx'
    df.to_excel(response, index=False)

    return response