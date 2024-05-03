from django.db import models
from User_Authentication.models import *
from category.models import *
from django.utils import timezone
from products.models import *

# Create your models here.

class WishList(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, null=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE,null=True)
    date_added = models.DateField(default=timezone.now)
