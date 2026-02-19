import os
from pathlib import Path
from urllib.parse import urlparse
from django.contrib import messages  # ← ADD THIS LINE!

try:
    import dj_database_url
except ImportError:
    dj_database_url = None

# CLOUDINARY - FREE MEDIA STORAGE (FIXES 404s)
try:
    from cloudinary import config
    from cloudinary.uploader import upload
    from cloudinary_storage.storage import VideoMediaCloudinaryStorage, ImageMediaCloudinaryStorage
    
    CLOUDINARY_STORAGE = {
        'CLOUD_NAME': os.getenv('CLOUDINARY_CLOUD_NAME'),
        'API_KEY': os.getenv('CLOUDINARY_API_KEY'),
        'API_SECRET': os.getenv('CLOUDINARY_API_SECRET'),
    }
    config(cloud_name=CLOUDINARY_STORAGE['CLOUD_NAME'],
           api_key=CLOUDINARY_STORAGE['API_KEY'],
           api_secret=CLOUDINARY_STORAGE['API_SECRET'])
    
    DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'
except ImportError:
    # Fallback for local dev
    pass

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY - Render production
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-local-key")
DEBUG = os.getenv("DJANGO_DEBUG", "False").strip().lower() in ("1", "true", "yes", "on")

# HOSTS - Render + naturalnikhaar.com
ALLOWED_HOSTS = ['*', 'naturalnikhaar.com', 'naturalnikhaar.onrender.com']

# Render auto-hostname
render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

# CSRF - Razorpay + Render
CSRF_TRUSTED_ORIGINS = []
for env_name in ("URL", "RENDER_EXTERNAL_URL"):
    raw = os.getenv(env_name)
    if raw:
        parsed = urlparse(raw)
        if parsed.scheme and parsed.netloc:
            CSRF_TRUSTED_ORIGINS.append(f"{parsed.scheme}://{parsed.netloc}")
CSRF_TRUSTED_ORIGINS.append("https://naturalnikhaar.com")

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth', 
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'cloudinary_storage',  # ADD THIS
    'ecommerceapp',
    'authcart',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # CRITICAL: FIRST!
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'ecommerce.urls'

TEMPLATES = [{
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
}]

WSGI_APPLICATION = 'ecommerce.wsgi.application'

# DATABASE - Railway PostgreSQL + Local SQLite
database_url = os.getenv("DATABASE_URL")
if database_url and dj_database_url:
    DATABASES = {"default": dj_database_url.parse(database_url, conn_max_age=600, ssl_require=True)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

# RAZORPAY - naturalnikhaar8316
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET", "")

# STATIC FILES - WHITENOISE PERFECT (CSS/JS WORKING)
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
STATICFILES_DIRS = [BASE_DIR / 'static']

# MEDIA FILES - CLOUDINARY (PERMANENT FIX)
MEDIA_URL = '/media/'
# No local MEDIA_ROOT needed - Cloudinary handles uploads

# SECURITY - PRODUCTION HTTPS
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000 if not DEBUG else 0
SECURE_HSTS_INCLUDE_SUBDOMAINS = True if not DEBUG else False
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

# LOGIN
LOGIN_URL = '/login/'
LOGOUT_URL = '/logout/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
MESSAGE_TAGS = {messages.ERROR: 'danger'}  # FIXED - NO COMMA!

# CLOUDINARY
CLOUDINARY_STORAGE = {
    'CLOUD_NAME': os.getenv("CLOUDINARY_CLOUD_NAME"),
    'API_KEY': os.getenv("CLOUDINARY_API_KEY"),
    'API_SECRET': os.getenv("CLOUDINARY_API_SECRET"),
}
DEFAULT_FILE_STORAGE = 'cloudinary_storage.storage.MediaCloudinaryStorage'  

# EMAILS - ORDER CONFIRMATIONS + CONTACT FORM
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.mailersend.net'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.getenv('SMTP_USERNAME')
EMAIL_HOST_PASSWORD = os.getenv('SMTP_PASSWORD')
DEFAULT_FROM_EMAIL = 'Natural Nikhaar <no-reply@yourdomain.com>'

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.getenv("REDIS_URL", "redis://127.0.0.1:6379"),
    }
}   

# SESSION ENGINE
SESSION_ENGINE = "django.contrib.sessions.backends.cache"
SESSION_CACHE_ALIAS = "default" 
