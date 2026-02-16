from django.contrib import admin
from django.urls import path, include, re_path
from django.conf.urls.static import static
from django.conf import settings
from django.views.static import serve
import os

# Default to serving media only in DEBUG mode unless explicitly enabled.
default_serve_media = "True" if settings.DEBUG else "False"
serve_media = os.getenv("DJANGO_SERVE_MEDIA", default_serve_media).strip().lower() in ("1", "true", "yes", "on")

urlpatterns = [
    # Keep media route first so uploaded files are always reachable in local/dev runs.
    # Disable in production by setting DJANGO_SERVE_MEDIA=False.
    *(
        [re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT})]
        if serve_media
        else []
    ),
    path('admin/', admin.site.urls),
    path('', include("ecommerceapp.urls")),
    path('auth/', include("authcart.urls")),
]

if settings.DEBUG or serve_media:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
