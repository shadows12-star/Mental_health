from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Assessment


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "predicted_score",
        "model_version",
        "created_at",
    )

    list_filter = ("created_at",)
    search_fields = ("user__username",)