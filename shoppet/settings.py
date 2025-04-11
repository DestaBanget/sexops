import os
from pathlib import Path
from django.core.management.utils import get_random_secret_key

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Determine which settings file to use based on environment variable
ENVIRONMENT = os.environ.get('DJANGO_ENVIRONMENT', 'local')

if ENVIRONMENT == 'production':
    print("Loading production settings...")
    from shoppet.settings_production import *
else:
    print("Loading local settings...")
    from shoppet.settings_local import *

# Any additional settings overrides can be added here

# SECURITY WARNING: keep the secret key used in production secret!
# In production, this should be set as an environment variable
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', get_random_secret_key())

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'  # Default to True for development

ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'crispy_forms',
    'crispy_bootstrap5',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'django_otp.plugins.otp_static',
    'axes',  # For login attempt throttling
    'django_extensions',  # Added django-extensions
    
    # Custom apps
    'accounts',
    'products',
    'cart',
    'orders',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',  # 2FA middleware
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',  # Should be the last middleware
    'csp.middleware.CSPMiddleware',  # Content Security Policy
]

# Axes Configuration (Login Throttling)
AUTHENTICATION_BACKENDS = [
    'axes.backends.AxesStandaloneBackend',
    'django.contrib.auth.backends.ModelBackend',
]

AXES_FAILURE_LIMIT = 5  # Number of login attempts before lockout
AXES_COOLOFF_TIME = 1  # Lockout time in hours
AXES_LOCKOUT_TEMPLATE = 'accounts/lockout.html'
AXES_LOCKOUT_URL = '/accounts/locked-out/'
# Remove the deprecated setting
# AXES_USE_USER_AGENT = True  # Track user agents for more accurate tracking

ROOT_URLCONF = 'shoppet.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'cart.context_processors.cart_processor',
            ],
        },
    },
]

WSGI_APPLICATION = 'shoppet.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,  # Database timeout
        }
    }
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 12,  # Increased from default 8
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'accounts.validators.SpecialCharacterValidator',  # Custom validator
    },
    {
        'NAME': 'accounts.validators.UpperLowerCaseValidator',  # Custom validator
    },
]

# Password Hashing
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.Argon2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'

# Fix the static files configuration
if DEBUG:
    STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
else:
    STATICFILES_DIRS = []  # Empty in production
    STATIC_ROOT = os.path.join(BASE_DIR, 'static')

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Crispy Forms
CRISPY_ALLOWED_TEMPLATE_PACKS = "bootstrap5"
CRISPY_TEMPLATE_PACK = "bootstrap5"

# Authentication settings
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = '/accounts/login/'

# Determine if we're in development or production
IS_DEVELOPMENT = DEBUG

# Session Security Settings - Adjusted for development
SESSION_COOKIE_SECURE = not IS_DEVELOPMENT  # Only enforce in production
SESSION_COOKIE_HTTPONLY = True  # Always prevent JavaScript access to session cookie
SESSION_COOKIE_SAMESITE = 'Lax'  # Restrict cookie sending to same-site requests
SESSION_EXPIRE_AT_BROWSER_CLOSE = True  # Session expires when browser closes
SESSION_COOKIE_AGE = 3600  # Session timeout in seconds (1 hour)

# CSRF Settings - Adjusted for development
CSRF_COOKIE_SECURE = not IS_DEVELOPMENT  # Only enforce in production
CSRF_COOKIE_HTTPONLY = True  # Always prevent JavaScript access to CSRF cookie
CSRF_COOKIE_SAMESITE = 'Lax'  # Restrict cookie sending to same-site requests
CSRF_FAILURE_VIEW = 'core.views.csrf_failure'  # Custom CSRF failure view

# Security Headers - Adjusted for development
SECURE_BROWSER_XSS_FILTER = not IS_DEVELOPMENT  # Enable browser XSS protection
SECURE_CONTENT_TYPE_NOSNIFF = not IS_DEVELOPMENT  # Prevent MIME type sniffing
SECURE_HSTS_SECONDS = 31536000 if not IS_DEVELOPMENT else 0  # 1 year HSTS in production
SECURE_HSTS_INCLUDE_SUBDOMAINS = not IS_DEVELOPMENT  # Include subdomains in HSTS
SECURE_HSTS_PRELOAD = not IS_DEVELOPMENT  # Allow preloading of HSTS
SECURE_SSL_REDIRECT = not IS_DEVELOPMENT  # Redirect HTTP to HTTPS only in production
SECURE_REFERRER_POLICY = 'same-origin'  # Restrict referrer information

# Content Security Policy - Relaxed for development
if IS_DEVELOPMENT:
    # More relaxed CSP for development
    CSP_DEFAULT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'")
    CSP_SCRIPT_SRC = ("'self'", "'unsafe-inline'", "'unsafe-eval'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    CSP_STYLE_SRC = ("'self'", "'unsafe-inline'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    CSP_FONT_SRC = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com", "data:")
    CSP_IMG_SRC = ("'self'", "data:", "https:", "blob:")
    CSP_CONNECT_SRC = ("'self'", "ws:", "wss:")
else:
    # Stricter CSP for production
    CSP_DEFAULT_SRC = ("'self'",)
    CSP_SCRIPT_SRC = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    CSP_STYLE_SRC = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    CSP_FONT_SRC = ("'self'", "https://cdn.jsdelivr.net", "https://cdnjs.cloudflare.com")
    CSP_IMG_SRC = ("'self'", "data:", "https:")
    CSP_CONNECT_SRC = ("'self'",)

# Email settings - Use console backend for development
if IS_DEVELOPMENT:
    EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
else:
    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
    EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
    EMAIL_USE_TLS = True
    EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
    EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
    DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@shoppet.com')

# Cart session ID
CART_SESSION_ID = 'cart'

# File upload restrictions
DATA_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 5242880  # 5MB
MEDIA_UPLOAD_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']

# Logging configuration
if not IS_DEVELOPMENT:
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
        },
        'handlers': {
            'file': {
                'level': 'WARNING',
                'class': 'logging.FileHandler',
                'filename': os.path.join(BASE_DIR, 'logs/django.log'),
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['file'],
                'level': 'WARNING',
                'propagate': True,
            },
        },
    }
    
    # Ensure directory exists
    os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
else:
    # Development logging to console
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console'],
                'level': 'INFO',
            },
        },
    }

# Override settings for local development
try:
    from shoppet.local_settings import *
except ImportError:
    pass
