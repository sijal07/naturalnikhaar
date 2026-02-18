"""
Django settings for ecommerce project - POSTGRESQL + RAZORPAY READY
COMPLETE PRODUCTION CONFIGURATION FOR RENDER + STATIC/IMAGES FIX
IMAGES/CAROUSEL LOADING AFTER WAKE-UP ✅
"""

import os
from importlib.util import find_spec
from pathlib import Path
from urllib.parse import urlparse
from django.contrib import messages

try:
    import dj_database_url
except ModuleNotFoundError:
    dj_database_url = None

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY: Production secret key override
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-!()tdsdll6ykd0r=7j#oi-@q9k@(mk70g=j7n%0lny^7hbakm*",
)

# SECURITY: Debug OFF in production
DEBUG = os.getenv("DJANGO_DEBUG", "False").strip().lower() in ("1", "true", "yes", "on")

# SECURITY: Allowed hosts for Render + Razorpay
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

# Render hostname support
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

# CSRF Trusted Origins for Render/Razorpay callbacks
CSRF_TRUSTED_ORIGINS = []
for env_name in ("URL", "DEPLOY_PRIME_URL", "DEPLOY_URL"):
    raw = os.getenv(env_name)
    if not raw:
        continue
    parsed = urlparse(raw)
    if parsed.scheme and parsed.netloc:
        CSRF_TRUSTED_ORIGINS.append(f"{parsed.scheme}://{parsed.netloc}")

render_external_url = os.getenv("RENDER_EXTERNAL_URL")
if render_external_url:
    parsed = urlparse(render_external_url)
    if parsed.scheme and parsed.netloc:
        CSRF_TRUSTED_ORIGINS.append(f"{parsed.scheme}://{parsed.netloc}")

CSRF_TRUSTED_ORIGINS = sorted(set(CSRF_TRUSTED_ORIGINS))

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'ecommerceapp',
    'authcart',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # ✅ FIXED: Always first for static
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'ecommerceapp.context_processors.admin_dashboard_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# 🚀 DATABASE: PostgreSQL (Render) + SQLite3 (Local VS Code)
database_url = os.getenv("DATABASE_URL")
if database_url and dj_database_url is not None:
    # Render PostgreSQL Production
    DATABASES = {
        "default": dj_database_url.parse(database_url, conn_max_age=600, ssl_require=True)
    }
else:
    # Local Development SQLite3
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# 💳 RAZORPAY CONFIGURATION (Environment Variables)
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# Add Razorpay callback hosts
if RAZORPAY_KEY_ID:
    razorpay_hosts = os.getenv("RAZORPAY_ALLOWED_HOSTS", "").split(",")
    for host in razorpay_hosts:
        host = host.strip()
        if host and host not in ALLOWED_HOSTS:
            ALLOWED_HOSTS.append(host)

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Email Configuration
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtpout.secureserver.net")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").strip().lower() in ("1", "true", "yes", "on")
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# 🔥 STATIC FILES - FIXED FOR RENDER (Images/Carousel/CSS/JS)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

# ✅ WhiteNoise Storage (Compress + Cache)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# 🔥 MEDIA FILES - PRODUCT IMAGES/CAROUSEL (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Custom message tags
MESSAGE_TAGS = {
    messages.ERROR: 'danger'
}

# SECURITY: Production settings
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True if not DEBUG else False
SECURE_HSTS_PRELOAD = True if not DEBUG else False
SESSION_COOKIE_SECURE = True if not DEBUG else False
CSRF_COOKIE_SECURE = True if not DEBUG else False

# Login/Logout URLs
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'
