from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
import uuid
from .models import *
from category.models import *
from products.models import *

# Create your models here.
class MyAccountManager(BaseUserManager):
    def create_user(self,username,email,phone_number,password=None):
        
        if not email:
            raise ValueError('you must have an email')
        
        if not username:
            raise ValueError('user must have a username')
        
        user=self.model(
            email=self.normalize_email(email),
            username=username,
            phone_number=phone_number
        )
        
        user.set_password(password)
        user.save(using=self.db)
        return user
    
    #creating custom superuser
    
    def create_superuser(self,username,email,password,phone_number):
        user=self.create_user(
            email=self.normalize_email(email),
            username=username,
            password=password,
            phone_number=phone_number
            
        )
            
        user.is_admin=True
        user.is_active=True
        user.is_staff=True
        user.is_superadmin=True
        user.save(using=self.db)
        return user        


class Account(AbstractBaseUser):
    first_name = models.CharField(max_length=100,default = 'no name')
    last_name = models.CharField(max_length=100,default = 'no name')
    username = models.CharField(max_length=100,  null=False)
    email = models.EmailField(null= False,unique=True)
    phone_number = models.CharField(max_length=20, null=True)
    is_active = models.BooleanField(default = False)
    is_blocked = models.BooleanField(default = False)
    
    #required
    date_joined=models.DateTimeField(auto_now_add=True)
    last_login=models.DateTimeField(auto_now_add=True)
    is_admin=models.BooleanField(default=False)
    is_active=models.BooleanField(default=True)
    is_staff=models.BooleanField(default=False)
    is_superadmin=models.BooleanField(default=False)
    is_emailverified = models.BooleanField(default = False)
    
    
    USERNAME_FIELD='email'
    REQUIRED_FIELDS=['username','phone_number']
    objects=MyAccountManager()
    
    def __str__(self):
        return self.email
    
    def has_perm(self,perm,obj=None):
        return self.is_admin
    
    def has_module_perms(self,add_label):
        return True
    
    def save(self, *args, **kwargs):
        if ' ' in self.username:
            self.first_name, self.last_name = self.username.split(' ', 1)
        else:
            self.first_name = self.username
            self.last_name = 'no name'
        super().save(*args, **kwargs)
    
class AddressBook(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE,null=True, default=None)
    first_name = models.CharField(max_length=50,null=True,blank=True)
    last_name = models.CharField(max_length=50,null=True,blank=True)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=100, default='example@example.com')
    address_line_1 = models.CharField(max_length=150,null=True,blank=True)
    address_line_2 = models.CharField(max_length=150,null=True,blank=True)
    country = models.CharField(max_length=50,null=True,blank=True)
    state = models.CharField(max_length=50,null=True,blank=True)
    city =models.CharField(max_length=50,null=True,blank=True)
    pincode = models.CharField(max_length=10,null=True,blank=True)
    is_default = models.BooleanField(default=False)

    def __str__(self):
        return self.first_name 
    
    
class UserProfile(models.Model):
    user = models.OneToOneField(Account, on_delete=models.CASCADE)
    otp_secret = models.CharField(max_length=16)  # Store the OTP secret key
    
    



class Payment(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=100)
    payment_method = models.CharField(max_length=100)
    amount_paid = models.CharField(max_length=100)
    status = models.CharField(max_length=100)
    discount = models.FloatField(default=0,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    
    def __str__(self):
        return self.payment_id





class Order(models.Model):
    STATUS = (
        ('New', 'New'),
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Cancelled', 'Cancelled'),
        ('Delivered', 'Delivered'),
        ('Returned', 'Returned'),
    )


    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order_number = models.CharField(max_length=20)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    email = models.EmailField(max_length=150)
    address_line_1 = models.CharField(max_length=150)
    address_line_2 = models.CharField(max_length=150)
    city = models.CharField(max_length=150)
    state = models.CharField(max_length=150)
    country = models.CharField(max_length=150)
    pincode = models.CharField(max_length=10)
    order_total = models.FloatField()
    tax = models.FloatField()
    status = models.CharField(max_length=10, choices=STATUS, default='New')
    ip = models.CharField(blank=True, max_length=20)
    is_ordered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    

    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    
    def full_address(self):
        return f"{self.address_line_1} {self.address_line_2}"
    
    # def __str__(self):
    #     return f'{self.order_total}'
    



class OrderProduct(models.Model):
    user = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_price = models.FloatField()
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True)
    variations = models.ManyToManyField(ProductVariant, blank=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ordered = models.BooleanField(default=False)
    color = models.CharField(max_length=50)
    size = models.CharField(max_length=50)


    @property
    def get_total(self):
        total = self.product_price * self.quantity
        return total
    
    

    