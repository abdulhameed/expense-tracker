from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.authentication.urls")),
    path("api/v1/", include("apps.projects.urls")),
    path("api/v1/", include("apps.transactions.urls")),
    path("api/v1/", include("apps.documents.urls")),
    path("api/v1/", include("apps.budgets.urls")),
    path("api/v1/", include("apps.reports.urls")),
    path("api/v1/", include("apps.activity.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
