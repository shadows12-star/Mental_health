from django.db import models

# Create your models here.

from django.db import models
from django.conf import settings


class WellnessRecommendation(models.Model):
    assessment = models.OneToOneField(
        "assessments.Assessment",
        on_delete=models.CASCADE,
        related_name="recommendation"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wellness_recommendations"
    )

    content = models.TextField()

    sources = models.JSONField(default=list)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"Recommendation for assessment {self.assessment_id}"




