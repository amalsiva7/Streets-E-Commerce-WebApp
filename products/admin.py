from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import *
from .forms import ProductImageForm
from django.shortcuts import render,redirect
from django.http import HttpResponseRedirect
# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_name', 'price', 'stock', 'category', 'modified_date', 'is_available')
    prepopulated_fields = {'slug': ('product_name',)}
    
class VariationAdmin(admin.ModelAdmin):
    list_display = ('product', 'size', 'stock', 'is_active')
    list_editable = ('is_active',)
    list_filter = list_display = ('product', 'size', 'is_active')
    
class BrandAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('brand_name',)}
    list_display = ('brand_name', 'slug')
  
class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1 
    fk_name = 'product'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]

    # Your other admin configurations for the Product model

    def add_bulk_images(self, request, queryset):
        form = None
        if 'apply' in request.POST:
            form = ProductImageForm(request.POST, request.FILES)
            if form.is_valid():
                for product in queryset:
                    image = form.cleaned_data['image']
                    ProductImage.objects.create(product=product, image=image)
                self.message_user(request, f'Bulk images added successfully for {queryset.count()} products.')
                return HttpResponseRedirect(request.get_full_path())

        if not form:
            form = ProductImageForm()

        return render(
            request,
            'admin/add_bulk_images.html',  # Create this template
            context={'products': queryset, 'form': form},
        )

    add_bulk_images.short_description = 'Add bulk images to selected products'

admin.site.add_action(ProductAdmin.add_bulk_images)    
# this will register the class to the site

# admin.site.register(Product)
admin.site.register(ProductImage) 
admin.site.register(Brand,BrandAdmin)
admin.site.register(ProductVariant, VariationAdmin)

