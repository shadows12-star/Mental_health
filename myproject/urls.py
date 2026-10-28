
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect


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
