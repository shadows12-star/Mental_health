
from django.conf.urls import static
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect



from django.conf import settings
from django.conf.urls.static import static
urlpatterns = [
    path("admin/", admin.site.urls),

    path("accounts/", include("accounts.urls")),

    path("dashboard/", include("dashboard.urls")),
    path(
        "assessments/",
        include("assessments.urls")
    ),
     path(
    "ai/",
    include("wellness_ai.urls")
    ),
    path("", lambda request: redirect("dashboard")),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )