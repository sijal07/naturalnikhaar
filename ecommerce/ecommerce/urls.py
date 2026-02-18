"""
ecommerce/urls.py - PRODUCTION READY MEDIA/STATIC SERVING
IMAGES/CAROUSEL WORK AFTER RENDER WAKE-UP ✅
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve
import os

# Serve media conditionally (local dev + Render free tier)
default_serve_media = "True"
SERVE_MEDIA = os.getenv("DJANGO_SERVE_MEDIA", default_serve_media).strip().lower() in ("1", "true", "yes", "on")

urlpatterns = [
    # ✅ MEDIA FIRST - Product images/carousel uploads
    *(
        [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
        if SERVE_MEDIA
        else []
    ),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps
    path('', include("ecommerceapp.urls")),
    path('auth/', include("authcart.urls")),
]

# ✅ STATIC/MEDIA DEVELOPMENT + RENDER FREE TIER
if settings.DEBUG or SERVE_MEDIA:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
