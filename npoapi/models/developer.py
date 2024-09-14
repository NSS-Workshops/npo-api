from django.conf import settings
from django.db import models


class Developer(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,  # Reference the custom user model
        on_delete=models.CASCADE,
        related_name="developer_profile",
    )
    # Add other fields for the Developer model as needed

    def __str__(self):
        return f"Developer: {self.user.username}"
