from django.urls import path
from . import views

urlpatterns = [
    path('checkout/', views.order_create, name='checkout'),
    path('confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('history/', views.order_list, name='order_list'),
]