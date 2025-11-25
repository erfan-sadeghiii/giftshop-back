# shop/utils.py
from .models import Cart

def get_or_create_cart(user):
    """Return the user's active cart, or create one if none exists."""
    cart, created = Cart.objects.get_or_create(user=user, status="pending")
    return cart
