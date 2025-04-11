from django.urls import path
from django.contrib.auth.views import LogoutView
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('password-change/', views.SecurePasswordChangeView.as_view(), name='password_change'),
    path('security/', views.security_settings, name='security_settings'),
    path('security/2fa/setup/', views.setup_2fa, name='setup_2fa'),
    path('security/2fa/disable/', views.disable_2fa, name='disable_2fa'),
    path('verify-2fa/', views.verify_2fa, name='verify_2fa'),
    path('locked-out/', views.lockout, name='lockout'),
]