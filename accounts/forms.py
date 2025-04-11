from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from captcha.fields import ReCaptchaField
from captcha.widgets import ReCaptchaV2Checkbox
from .models import Profile
import os

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("This email address is already in use.")
        return email

class UserLoginForm(AuthenticationForm):
    username = forms.CharField(label='Email / Username')
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)
    
    class Meta:
        model = User
        fields = ['username', 'password']

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError("This email address is already in use.")
        return email

class ProfileUpdateForm(forms.ModelForm):
    profile_image = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        error_messages={'invalid': "Image files only"},
        help_text="Upload a profile picture (JPG, PNG, GIF)"
    )
    
    class Meta:
        model = Profile
        fields = ['address', 'city', 'state', 'zip_code', 'profile_image']
        
    def clean_zip_code(self):
        zip_code = self.cleaned_data.get('zip_code')
        # Basic ZIP code validation
        if zip_code and not zip_code.isdigit():
            raise ValidationError("ZIP code should contain only digits.")
        return zip_code
    
    def clean_profile_image(self):
        image = self.cleaned_data.get('profile_image')
        if image:
            # Check file size
            if image.size > 5 * 1024 * 1024:  # 5MB limit
                raise ValidationError("Image file too large ( > 5MB )")
            
            # Check file extension
            ext = os.path.splitext(image.name)[1].lower()
            if ext not in ['.jpg', '.jpeg', '.png', '.gif']:
                raise ValidationError("Unsupported file extension. Use JPG, PNG or GIF.")
        
        return image

class SecurePasswordChangeForm(PasswordChangeForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox)

class TwoFactorSetupForm(forms.Form):
    verification_code = forms.CharField(
        max_length=6,
        min_length=6,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter 6-digit code'})
    )
