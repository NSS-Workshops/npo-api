from django.conf import settings
from django.db import models
from django.contrib.auth.models import Group


class Developer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Use the custom user model instead of 'auth.User'
        on_delete=models.CASCADE,
        related_name="developer_profile",
    )
    # Add other fields for the Developer model as needed

    def __str__(self):
        return f"Developer: {self.user.username}"
