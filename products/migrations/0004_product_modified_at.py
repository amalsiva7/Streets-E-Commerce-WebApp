# Generated by Django 5.0.1 on 2024-03-04 07:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0003_alter_product_product_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='modified_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
