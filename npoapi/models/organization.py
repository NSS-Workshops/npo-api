from django.db import models
from django.conf import settings  # Import settings to reference the user model
from django.contrib.auth.models import Group


class Organization(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    # Use ForeignKey to reference the default user model
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Use the default user model
        on_delete=models.CASCADE,
        related_name="organizations",
        null=True,
        blank=True,
    )

    class Meta:
        permissions = [
            ("can_manage_organization", "Can manage organization details"),
            ("can_manage_users", "Can manage users"),
        ]

    def __str__(self):
        return self.name
