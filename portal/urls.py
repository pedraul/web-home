from django.conf import settings
from django.contrib import admin
from django.urls import include, path, re_path
from django.views.static import serve


urlpatterns = [
    path("admin/", admin.site.urls),
    # Uploaded images (logo, slides, service pictures). Served by Django even when
    # DEBUG is False, so they still show on PythonAnywhere if no /media/ mapping exists.
    re_path(r"^media/(?P<path>.*)$", serve, {"document_root": settings.MEDIA_ROOT}),
    path("", include("services.urls")),
]
