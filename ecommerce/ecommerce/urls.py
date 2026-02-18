"""
ecommerce/urls.py - RENDER FREE TIER ✅ MEDIA IMAGES LOADING
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.views.static import serve

# FORCE MEDIA FOR RENDER FREE TIER
SERVE_MEDIA = True

urlpatterns = [
    # 🔥 PRODUCT IMAGES FIRST (FIXED 404s)
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # Apps
    path('', include("ecommerceapp.urls")),
    path('auth/', include("authcart.urls")),
]

# STATIC fallback (local only)
if settings.DEBUG:
    from django.conf.urls.static import static
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
