from decimal import Decimal
from django.conf import settings
from products.models import Product
import bleach
from django.contrib.auth.models import User
from .models import CartItem

class Cart:
    def __init__(self, request):
        """
        Initialize the cart.
        """
        self.session = request.session
        self.user = request.user
        
        # For authenticated users, use database-backed cart
        if self.user.is_authenticated:
            # Get cart from database or create empty cart
            self.cart = self._get_cart_from_db()
        else:
            # Get cart from session or create empty cart
            cart = self.session.get(settings.CART_SESSION_ID)
            if not cart:
                # Save an empty cart in the session
                cart = self.session[settings.CART_SESSION_ID] = {}
            self.cart = cart
    
    def _get_cart_from_db(self):
        """
        Get cart items from database and convert to session format.
        """
        cart = {}
        cart_items = CartItem.objects.filter(user=self.user).select_related('product')
        
        for item in cart_items:
            cart[str(item.product.id)] = {
                'quantity': item.quantity,
                'price': str(item.product.price)
            }
        
        return cart
    
    def add(self, product, quantity=1, override_quantity=False):
        """
        Add a product to the cart or update its quantity.
        """
        product_id = str(product.id)
        
        # Validate product and quantity
        if not isinstance(product, Product):
            return False
        
        try:
            quantity = int(quantity)
            if quantity <= 0:
                return False
        except (ValueError, TypeError):
            return False
        
        # Check stock availability
        if quantity > product.stock:
            quantity = product.stock
        
        # For authenticated users, update database
        if self.user.is_authenticated:
            cart_item, created = CartItem.objects.get_or_create(
                user=self.user,
                product=product,
                defaults={'quantity': 0}
            )
            
            if override_quantity:
                cart_item.quantity = quantity
            else:
                cart_item.quantity += quantity
            
            cart_item.save()
            
            # Update local cart
            self.cart = self._get_cart_from_db()
        else:
            # Update session cart
            if product_id not in self.cart:
                self.cart[product_id] = {'quantity': 0, 'price': str(product.price)}
            
            if override_quantity:
                self.cart[product_id]['quantity'] = quantity
            else:
                self.cart[product_id]['quantity'] += quantity
            
            self.save()
        
        return True
    
    def save(self):
        # Only save to session if user is not authenticated
        if not self.user.is_authenticated:
            # Mark the session as "modified" to make sure it gets saved
            self.session.modified = True
    
    def remove(self, product):
        """
        Remove a product from the cart.
        """
        product_id = str(product.id)
        
        # For authenticated users, remove from database
        if self.user.is_authenticated:
            CartItem.objects.filter(user=self.user, product=product).delete()
            # Update local cart
            self.cart = self._get_cart_from_db()
        else:
            # Remove from session cart
            if product_id in self.cart:
                del self.cart[product_id]
                self.save()
    
    def __iter__(self):
        """
        Iterate over the items in the cart and get the products from the database.
        """
        product_ids = self.cart.keys()
        # Get the product objects and add them to the cart
        products = Product.objects.filter(id__in=product_ids)
        
        cart = self.cart.copy()
        for product in products:
            cart[str(product.id)]['product'] = product
        
        for item in cart.values():
            item['price'] = Decimal(item['price'])
            item['total_price'] = item['price'] * item['quantity']
            yield item
    
    def __len__(self):
        """
        Count all items in the cart.
        """
        return sum(item['quantity'] for item in self.cart.values())
    
    def get_total_price(self):
        return sum(Decimal(item['price']) * item['quantity'] for item in self.cart.values())
    
    def clear(self):
        # For authenticated users, clear database cart
        if self.user.is_authenticated:
            CartItem.objects.filter(user=self.user).delete()
            # Update local cart
            self.cart = {}
        else:
            # Remove cart from session
            del self.session[settings.CART_SESSION_ID]
            self.save()
