import os
from pathlib import Path
from urllib.parse import urlparse

from django.contrib import messages

# BASE DIR
BASE_DIR = Path(__file__).resolve().parent.parent

# SECRET & DEBUG
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY", "django-insecure-local-key-do-not-use-in-production"
)
# Respect env in production; default to True for local runs.
DEBUG = os.getenv("DJANGO_DEBUG", "True").strip().lower() == "true"

# HOSTS
default_hosts = "naturalnikhaar.com,naturalnikhaar.onrender.com,localhost,127.0.0.1"
ALLOWED_HOSTS = [
    h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", os.getenv("ALLOWED_HOSTS", default_hosts)).split(",") if h.strip()
]

# APPS
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",
    # 3rd Party
    "cloudinary",
    "cloudinary_storage",
    # Local
    "ecommerceapp",
    "authcart",
]

# MIDDLEWARE
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ecommerce.urls"

# TEMPLATES
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ecommerce.wsgi.application"

# DATABASE – default SQLite
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

# PostgreSQL for Render (Railway URL)
try:
    import dj_database_url

    if os.getenv("DATABASE_URL"):
        DATABASES["default"] = dj_database_url.parse(
            os.getenv("DATABASE_URL"), conn_max_age=600
        )
except ImportError:
    pass

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Kolkata"
USE_I18N = True
USE_TZ = True

# Static files
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Media (Cloudinary)
MEDIA_URL = "/media/"
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"

CLOUDINARY_STORAGE = {
    "CLOUD_NAME": os.getenv("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": os.getenv("CLOUDINARY_API_KEY"),
    "API_SECRET": os.getenv("CLOUDINARY_API_SECRET"),
}

# Authentication
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/auth/login/"

# Messages
MESSAGE_TAGS = {
    messages.DEBUG: "debug",
    messages.INFO: "info",
    messages.SUCCESS: "success",
    messages.WARNING: "warning",
    messages.ERROR: "danger",
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = not DEBUG
CSRF_TRUSTED_ORIGINS = [
    "https://naturalnikhaar.com",
    "https://naturalnikhaar.onrender.com",
]

# ========= EMAIL CONFIG (MailerSend SMTP) =========
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = os.getenv("EMAIL_HOST", "smtp.mailersend.net")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", 587))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "true").strip().lower() == "true"
EMAIL_TIMEOUT = int(os.getenv("EMAIL_TIMEOUT", "10"))

EMAIL_HOST_USER = os.getenv("SMTP_USERNAME") or os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("SMTP_PASSWORD") or os.getenv("EMAIL_HOST_PASSWORD", "")

DEFAULT_FROM_EMAIL = os.getenv(
    "DEFAULT_FROM_EMAIL", "Natural Nikhaar <no-reply@naturalnikhaar.com>"
)

# Optional console backend switch (you can ignore for local)
if os.getenv("USE_CONSOLE_EMAIL", "false").strip().lower() == "true":
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Razorpay
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID", "")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET", "")

# ========== LOGGING FOR DEBUGGING 500 ERRORS ==========
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] {asctime} {module} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "debug.log",
            "formatter": "verbose",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}
