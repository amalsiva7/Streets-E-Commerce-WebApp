from django.db import models
from User_Authentication.models import *

# Create your models here.
class Coupon(models.Model):
    coupon_code = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    coupon_discount = models.IntegerField(null=False)
    min_purchase = models.IntegerField(null=False)
    coupon_expiry = models.DateField(null=False)
    
    def is_redeemed_by_user(self, user):
        # Check if the coupon has been redeemed by the given user
        return self.user_coupon_set.filter(user=user).exists()
    
    
class User_Coupon(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE)
    coupon_code = models.ForeignKey(Coupon, on_delete=models.CASCADE)
    is_redeemed = models.BooleanField(default=False)
    
    
    