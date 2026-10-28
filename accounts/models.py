from django.db import models

# Create your models here.

from django.conf import settings
from django.db import models


def profile_picture_upload_path(instance, filename):
    """
    Store profile pictures in a user-specific folder.
    """
    return f"profile_pictures/user_{instance.user_id}/{filename}"


class UserProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )

    profile_picture = models.ImageField(
        upload_to=profile_picture_upload_path,
        blank=True,
        null=True,
    )

    bio = models.CharField(
        max_length=250,
        blank=True,
    )

    date_of_birth = models.DateField(
        blank=True,
        null=True,
    )

    location = models.CharField(
        max_length=100,
        blank=True,
    )

    updated_at = models.DateTimeField(
        auto_now=True,
    )

    def __str__(self):
        return f"Profile for {self.user.username}"
