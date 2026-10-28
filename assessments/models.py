

# Create your models here.

from django.db import models
from django.conf import settings


class Assessment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="assessments"
    )

    # Assessment input data
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    academic_level = models.CharField(max_length=100)
    most_used_platform = models.CharField(max_length=100)
    purpose_of_use = models.CharField(max_length=100)

    avg_daily_usage_hours = models.FloatField()
    daily_unlocks = models.PositiveIntegerField()
    physical_activity_hours = models.FloatField()
    sleep_hours_per_night = models.FloatField()
    study_hours = models.FloatField()
    stress_level = models.CharField(max_length=20)

    # Prediction result
    predicted_score = models.FloatField()
    model_version = models.CharField(
        max_length=20,
        default="1.0"
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"{self.user.username} - "
            f"{self.predicted_score}"
        )
