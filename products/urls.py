from django.urls import path
from . import views

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('search/', views.search_products, name='search_products'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
]
