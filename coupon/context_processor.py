from django.db.models import F, FloatField, ExpressionWrapper
from django.db.models.functions import Abs  # Import Abs function
from .models import Product

def deducted_price(request):
    # Your logic to calculate deducted price
    products_with_deducted_price = Product.objects.annotate(
        deducted_price=ExpressionWrapper(
            Abs(F('rprice') - F('price')),  # Use Abs function to ensure positive value
            output_field=FloatField()
        )
    )
    print(products_with_deducted_price,"***************************************Inside the CONTEXT PROCESSOR***************************************")
    return {'deducted_price': products_with_deducted_price}
