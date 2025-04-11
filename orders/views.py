from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.db import transaction
from django.core.exceptions import PermissionDenied
from django.utils.crypto import get_random_string
import bleach
from decimal import Decimal

from .models import OrderItem, Order
from .forms import OrderCreateForm
from cart.cart import Cart
from products.models import Product

@login_required
@require_http_methods(["GET", "POST"])
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, 'Your cart is empty')
        return redirect('cart_detail')
    
    # Pre-fill form with user data if available
    initial_data = {}
    if hasattr(request.user, 'profile'):
        initial_data = {
            'full_name': f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username,
            'email': request.user.email,
            'address': request.user.profile.address or '',
            'city': request.user.profile.city or '',
            'state': request.user.profile.state or '',
            'zip_code': request.user.profile.zip_code or '',
        }
    
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total_amount = cart.get_total_price() + Decimal('10.00')  # Add shipping
                    order.ip_address = request.META.get('REMOTE_ADDR')
                    order.transaction_id = get_random_string(32)
                    order.save()
                    
                    # Create order items and update product stock
                    for item in cart:
                        product = item['product']
                        if product.stock >= item['quantity']:
                            OrderItem.objects.create(
                                order=order,
                                product=product,
                                price=item['price'],
                                quantity=item['quantity']
                            )
                            # Update product stock
                            product.stock -= item['quantity']
                            product.save()
                        else:
                            # Not enough stock, rollback transaction
                            messages.error(request, f"Not enough stock for {product.name}. Available: {product.stock}")
                            raise Exception("Insufficient stock")
                    
                    # Clear the cart
                    cart.clear()
                    
                    return redirect('order_confirmation', order_id=order.id)
            except Exception as e:
                messages.error(request, f"Error processing order: {str(e)}")
                return redirect('cart_detail')
    else:
        form = OrderCreateForm(initial=initial_data)
    
    return render(request, 'orders/checkout.html', {
        'cart': cart,
        'form': form
    })

@login_required
@require_http_methods(["GET"])
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_confirmation.html', {'order': order})

@login_required
@require_http_methods(["GET"])
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'orders/order_detail.html', {'order': order})

@login_required
@require_http_methods(["GET"])
def order_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
@require_http_methods(["POST"])
def cancel_order(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    
    # Only allow cancellation of pending orders
    if order.status != 'pending':
        messages.error(request, 'Only pending orders can be cancelled.')
        return redirect('order_detail', order_id=order.id)
    
    # Update order status
    order.status = 'cancelled'
    order.save()
    
    # Restore product stock
    for item in order.items.all():
        product = item.product
        product.stock += item.quantity
        product.save()
    
    messages.success(request, 'Your order has been cancelled.')
    return redirect('order_list')
