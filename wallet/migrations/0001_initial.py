# Generated by Django 5.0.1 on 2024-04-06 07:25

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('User_Authentication', '0008_account_referral_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('description', models.TextField()),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('transaction_type', models.CharField(max_length=50)),
                ('user', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='User_Authentication.userprofile')),
            ],
        ),
    ]
