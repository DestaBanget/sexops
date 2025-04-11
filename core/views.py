from django.shortcuts import render
from django.http import HttpResponseForbidden
from django.views.decorators.http import require_http_methods
from products.models import Product, Category

@require_http_methods(["GET"])
def home(request):
    featured_products = Product.objects.filter(featured=True)[:4]
    categories = Category.objects.all()
    
    return render(request, 'core/home.html', {
        'featured_products': featured_products,
        'categories': categories
    })

@require_http_methods(["GET"])
def about(request):
    return render(request, 'core/about.html')

@require_http_methods(["GET"])
def contact(request):
    return render(request, 'core/contact.html')

def csrf_failure(request, reason=""):
    return render(request, 'core/csrf_failure.html', {'reason': reason}, status=403)

def handler404(request, exception):
    return render(request, 'core/404.html', status=404)

def handler500(request):
    return render(request, 'core/500.html', status=500)

def handler403(request, exception):
    return render(request, 'core/403.html', status=403)