from django.db import models
from .custom_user import CustomUser  # Import the CustomUser model


class Organization(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)

    # Use ForeignKey if multiple users can belong to one organization
    user = models.ForeignKey(
        CustomUser,
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
