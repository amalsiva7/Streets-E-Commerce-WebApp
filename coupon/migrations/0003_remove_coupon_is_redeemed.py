# Generated by Django 5.0.1 on 2024-04-04 03:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('coupon', '0002_coupon_is_redeemed'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='coupon',
            name='is_redeemed',
        ),
    ]