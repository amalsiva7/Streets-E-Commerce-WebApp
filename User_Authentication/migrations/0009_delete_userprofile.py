# Generated by Django 5.0.1 on 2024-04-08 10:10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('User_Authentication', '0008_account_referral_id'),
        ('wallet', '0002_alter_transaction_user'),
    ]

    operations = [
        migrations.DeleteModel(
            name='UserProfile',
        ),
    ]