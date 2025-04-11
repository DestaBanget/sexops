from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView, PasswordChangeView
from django.contrib.auth import login, update_session_auth_hash
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.http import HttpResponseRedirect
from django_otp.plugins.otp_totp.models import TOTPDevice
from django_otp.util import random_hex
import qrcode
import qrcode.image.svg
from io import BytesIO
import base64

from .forms import (
    UserRegisterForm, UserLoginForm, UserUpdateForm, 
    ProfileUpdateForm, SecurePasswordChangeForm, TwoFactorSetupForm
)
from .models import LoginAttempt
from orders.models import Order

class CustomLoginView(LoginView):
    authentication_form = UserLoginForm
    template_name = 'accounts/login.html'
    
    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Get user IP and user agent
        ip = self.request.META.get('REMOTE_ADDR', '')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Record successful login attempt
        LoginAttempt.objects.create(
            user=form.get_user(),
            username=form.cleaned_data.get('username'),
            ip_address=ip,
            user_agent=user_agent,
            successful=True
        )
        
        # Update user profile with last login IP
        user = form.get_user()
        user.profile.last_login_ip = ip
        user.profile.login_attempts = 0  # Reset login attempts
        user.profile.save()
        
        messages.success(self.request, 'You have been logged in successfully!')
        
        # Check if 2FA is enabled
        if user.profile.two_factor_enabled:
            # Store user ID in session for 2FA verification
            self.request.session['user_id_for_2fa'] = user.id
            return HttpResponseRedirect(reverse_lazy('verify_2fa'))
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # Get username, IP and user agent
        username = form.cleaned_data.get('username', '')
        ip = self.request.META.get('REMOTE_ADDR', '')
        user_agent = self.request.META.get('HTTP_USER_AGENT', '')
        
        # Record failed login attempt
        LoginAttempt.objects.create(
            username=username,
            ip_address=ip,
            user_agent=user_agent,
            successful=False
        )
        
        return super().form_invalid(form)

@sensitive_post_parameters()
@csrf_protect
@never_cache
def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'accounts/profile.html', {'orders': orders})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)
    
    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'accounts/edit_profile.html', context)

class SecurePasswordChangeView(PasswordChangeView):
    form_class = SecurePasswordChangeForm
    template_name = 'accounts/password_change.html'
    success_url = reverse_lazy('profile')
    
    def form_valid(self, form):
        messages.success(self.request, 'Your password has been updated!')
        update_session_auth_hash(self.request, form.user)
        return super().form_valid(form)

@login_required
def security_settings(request):
    user = request.user
    has_2fa = user.profile.two_factor_enabled
    
    return render(request, 'accounts/security_settings.html', {
        'has_2fa': has_2fa
    })

@login_required
def setup_2fa(request):
    # Check if user already has 2FA enabled
    if request.user.profile.two_factor_enabled:
        messages.warning(request, 'Two-factor authentication is already enabled.')
        return redirect('security_settings')
    
    # Get or create TOTP device
    device, created = TOTPDevice.objects.get_or_create(
        user=request.user,
        name='default',
        defaults={'key': random_hex(20)}
    )
    
    # Generate QR code
    config_url = device.config_url
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(config_url)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer)
    qr_code_image = base64.b64encode(buffer.getvalue()).decode()
    
    if request.method == 'POST':
        form = TwoFactorSetupForm(request.POST)
        if form.is_valid():
            verification_code = form.cleaned_data['verification_code']
            
            # Verify the code
            if device.verify_token(verification_code):
                # Enable 2FA
                request.user.profile.two_factor_enabled = True
                request.user.profile.save()
                
                messages.success(request, 'Two-factor authentication has been enabled successfully!')
                return redirect('security_settings')
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
    else:
        form = TwoFactorSetupForm()
    
    return render(request, 'accounts/setup_2fa.html', {
        'form': form,
        'qr_code_image': qr_code_image,
        'secret_key': device.key
    })

@login_required
def disable_2fa(request):
    # Check if user has 2FA enabled
    if not request.user.profile.two_factor_enabled:
        messages.warning(request, 'Two-factor authentication is not enabled.')
        return redirect('security_settings')
    
    if request.method == 'POST':
        # Disable 2FA
        request.user.profile.two_factor_enabled = False
        request.user.profile.save()
        
        # Delete TOTP devices
        TOTPDevice.objects.filter(user=request.user).delete()
        
        messages.success(request, 'Two-factor authentication has been disabled.')
        return redirect('security_settings')
    
    return render(request, 'accounts/disable_2fa.html')

@never_cache
def verify_2fa(request):
    user_id = request.session.get('user_id_for_2fa')
    
    if not user_id:
        messages.error(request, 'Authentication error. Please login again.')
        return redirect('login')
    
    if request.method == 'POST':
        verification_code = request.POST.get('verification_code')
        
        try:
            user = User.objects.get(id=user_id)
            device = TOTPDevice.objects.get(user=user, name='default')
            
            if device.verify_token(verification_code):
                # Complete login process
                login(request, user)
                
                # Clear 2FA session data
                if 'user_id_for_2fa' in request.session:
                    del request.session['user_id_for_2fa']
                
                messages.success(request, 'Two-factor authentication successful!')
                
                # Redirect to intended page or default
                next_url = request.session.get('next', 'home')
                if 'next' in request.session:
                    del request.session['next']
                
                return redirect(next_url)
            else:
                messages.error(request, 'Invalid verification code. Please try again.')
        except (User.DoesNotExist, TOTPDevice.DoesNotExist):
            messages.error(request, 'Authentication error. Please login again.')
            return redirect('login')
    
    return render(request, 'accounts/verify_2fa.html')

def lockout(request):
    return render(request, 'accounts/lockout.html')
