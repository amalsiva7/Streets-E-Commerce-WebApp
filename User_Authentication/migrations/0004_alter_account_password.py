# Generated by Django 5.0.1 on 2024-02-07 10:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('User_Authentication', '0003_alter_account_password'),
    ]

    operations = [
        migrations.AlterField(
            model_name='account',
            name='password',
            field=models.CharField(max_length=128, verbose_name='password'),
        ),
    ]
