from django.db import models
from django.contrib.auth.models import AbstractBaseUser,BaseUserManager
from django.utils.text import slugify
from category.models import Category

# Create your models here.

class Brand(models.Model):
    brand_name = models.CharField(max_length=100,unique=True)
    slug = models.SlugField(unique=False,null=True,blank=True)
    
    def __str__(self):
        return self.brand_name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True,default=1000)
    product_name = models.CharField(max_length=100,null=False,blank=False,unique=True)
    category = models.ForeignKey(Category,on_delete=models.CASCADE)
    brand = models.ForeignKey(Brand,on_delete=models.CASCADE)
    description = models.TextField()
    price = models.IntegerField()
    image = models.ImageField(upload_to='product_images/',null=True, blank= True)
    is_active = models.BooleanField(default=True)
    resale_price = models.IntegerField(null=True)
    modified_at = models.DateTimeField(auto_now=True)
    rprice = models.DecimalField(max_digits=10, decimal_places=2,null=True,default=0.00)
    
    def __str__(self):
        return self.product_name
    
    def save(self, *args, **kwargs):
        if self.pk is None:  # Only execute if the product is being created (not updated)
            last_product_id = Product.objects.order_by('-product_id').first()
            if last_product_id:
                self.product_id = last_product_id.product_id + 1  # Increment the product_id
            else:
                self.product_id = 1000  # Start from 1000 if no products exist yet
        if int(self.price) < 0:
            raise ValueError("Price cannot be negative.")
        super().save(*args, **kwargs)
    
    
class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name = 'images')
    image = models.ImageField('photos/product')
    
    def __str__(self):
        if self.product:
            return f"Product: {self.product.brand},{self.product.category}"
        else:
            return "Product : N/A"
   
        
class VariationManager(models.Manager):
    def sizes(self):
        return self.filter(is_active=True).values_list('size', flat=True).distinct()

    def variants_by_size(self, size):
        return self.filter(size=size, is_active=True)
    
SIZE_CHOICES = [
    ('s','S'),
    ('m','M'),
    ('l','L'),
]


class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    size = models.CharField(max_length=100, choices=SIZE_CHOICES)
    stock = models.PositiveIntegerField(default=0)
    # price = models.DecimalField(max_digits=10, decimal_places=2)
    created_date = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    objects = VariationManager()
    
    def __str__(self):
        return f"{self.product.product_name}, Size: {self.size}"
    
