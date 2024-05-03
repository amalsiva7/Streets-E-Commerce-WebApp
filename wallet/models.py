from django.db import models
from User_Authentication.models import *

# Create your models here.


class Transaction(models.Model):
    user = models.ForeignKey(Account, on_delete=models.CASCADE, default=1)
    date = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=False)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(max_length=50)