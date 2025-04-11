from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.views.decorators.http import require_http_methods
from django.core.exceptions import PermissionDenied
from django.utils.text import slugify
import bleach

from .models import Product, Category, Review
from .forms import ReviewForm

def product_list(request):
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category)
    else:
        products = Product.objects.all()
    
    categories = Category.objects.all()
    
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'current_category': category_slug
    })

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    reviews = Review.objects.filter(product=product).order_by('-created_at')
    
    # Handle review submission
    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            # Check if user already reviewed this product
            existing_review = Review.objects.filter(product=product, user=request.user).first()
            
            if existing_review:
                # Update existing review
                existing_review.rating = form.cleaned_data['rating']
                existing_review.comment = bleach.clean(form.cleaned_data['comment'])
                existing_review.save()
                messages.success(request, 'Your review has been updated!')
            else:
                # Create new review
                review = form.save(commit=False)
                review.product = product
                review.user = request.user
                review.comment = bleach.clean(review.comment)
                review.save()
                messages.success(request, 'Your review has been submitted!')
            
            return redirect('product_detail', slug=slug)
    else:
        form = ReviewForm()
    
    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form
    })

def search_products(request):
    query = bleach.clean(request.GET.get('query', ''))
    category = bleach.clean(request.GET.get('category', ''))
    min_price = bleach.clean(request.GET.get('min_price', ''))
    max_price = bleach.clean(request.GET.get('max_price', ''))
    
    products = Product.objects.all()
    
    if query:
        products = products.filter(Q(name__icontains=query) | Q(description__icontains=query))
    
    if category:
        products = products.filter(category__slug=category)
    
    if min_price:
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    
    if max_price:
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass
    
    categories = Category.objects.all()
    
    return render(request, 'products/search_results.html', {
        'products': products,
        'query': query,
        'category': category,
        'min_price': min_price,
        'max_price': max_price,
        'categories': categories
    })

@login_required
@require_http_methods(["POST"])
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    
    # Check if the user is the owner of the review
    if review.user != request.user:
        raise PermissionDenied
    
    product_slug = review.product.slug
    review.delete()
    
    messages.success(request, 'Your review has been deleted.')
    return redirect('product_detail', slug=product_slug)
