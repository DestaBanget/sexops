from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView
from django.contrib.sitemaps.views import sitemap
from django.contrib.sitemaps import GenericSitemap
from products.models import Product, Category
from core.sitemaps import StaticViewSitemap

# Define sitemaps
sitemaps = {
    'static': StaticViewSitemap,
    'products': GenericSitemap({
        'queryset': Product.objects.all(),
        'date_field': 'updated_at',
    }, priority=0.7),
    'categories': GenericSitemap({
        'queryset': Category.objects.all(),
    }, priority=0.5),
}

# Admin site customization
admin.site.site_header = 'ShopPet Administration'
admin.site.site_title = 'ShopPet Admin'
admin.site.index_title = 'ShopPet Management'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('accounts/', include('accounts.urls')),
    path('products/', include('products.urls')),
    path('cart/', include('cart.urls')),
    path('orders/', include('orders.urls')),
    
    # Security and SEO
    path('robots.txt', TemplateView.as_view(template_name="robots.txt", content_type="text/plain")),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    path('security.txt', TemplateView.as_view(template_name="security.txt", content_type="text/plain")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom error handlers
handler404 = 'core.views.handler404'
handler500 = 'core.views.handler500'
handler403 = 'core.views.handler403'