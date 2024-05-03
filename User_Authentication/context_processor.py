from cart.models import *
from wishlist.models import *

def count_num(request):
  cart_items_count = 0
  wishlist_items_count = 0
  if request.user.is_authenticated:
        cart_items_count = CartItem.objects.filter(user=request.user, is_active=True).count()
        wishlist_items_count = WishList.objects.filter(user=request.user).count()
        
  context={'cart_count':cart_items_count,
        'wishlist_count':wishlist_items_count}
  
  return context