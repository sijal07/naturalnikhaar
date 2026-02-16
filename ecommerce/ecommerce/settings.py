"""
Django settings for ecommerce project.
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


# Keep local default for backward compatibility; override in production with DJANGO_SECRET_KEY.
SECRET_KEY = os.getenv(
    "DJANGO_SECRET_KEY",
    "django-insecure-!()tdsdll6ykd0r=7j#oi-@q9k@(mk70g=j7n%0lny^7hbakm*",
)

# Requested production default.
DEBUG = os.getenv("DJANGO_DEBUG", "False").strip().lower() in ("1", "true", "yes", "on")

# Requested permissive host default; can be overridden via env.
ALLOWED_HOSTS = [h.strip() for h in os.getenv("DJANGO_ALLOWED_HOSTS", "*").split(",") if h.strip()]
if not ALLOWED_HOSTS:
    ALLOWED_HOSTS = ["*"]

render_hostname = os.getenv("RENDER_EXTERNAL_HOSTNAME")
if render_hostname and render_hostname not in ALLOWED_HOSTS and "*" not in ALLOWED_HOSTS:
    ALLOWED_HOSTS.append(render_hostname)

# Netlify environment URL support for CSRF trusted origins.
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
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

WHITENOISE_INSTALLED = find_spec("whitenoise") is not None
if WHITENOISE_INSTALLED:
    MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')

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


# Database
# Defaults to sqlite for local compatibility; supports external DB via env vars.
db_engine = os.getenv("DB_ENGINE")
database_url = os.getenv("DATABASE_URL")
if database_url and dj_database_url is not None:
    DATABASES = {"default": dj_database_url.parse(database_url, conn_max_age=600, ssl_require=True)}
elif db_engine:
    DATABASES = {
        "default": {
            "ENGINE": db_engine,
            "NAME": os.getenv("DB_NAME", ""),
            "USER": os.getenv("DB_USER", ""),
            "PASSWORD": os.getenv("DB_PASSWORD", ""),
            "HOST": os.getenv("DB_HOST", ""),
            "PORT": os.getenv("DB_PORT", ""),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }


# Password validation
# https://docs.djangoproject.com/en/3.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/3.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# sending emails

EMAIL_HOST = os.getenv("EMAIL_HOST", "smtpout.secureserver.net")
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "True").strip().lower() in ("1", "true", "yes", "on")
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'



STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']
if WHITENOISE_INSTALLED:
    # Use non-manifest storage by default to avoid runtime 500s from missing
    # manifest entries on platforms where static assets may drift across deploys.
    STATICFILES_STORAGE = os.getenv(
        "DJANGO_STATICFILES_STORAGE",
        "whitenoise.storage.CompressedStaticFilesStorage",
    )

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


MESSAGE_TAGS = {
    messages.ERROR:'danger'
}
