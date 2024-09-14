from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Define role choices
    ROLE_CHOICES = (
        ("admin", "Admin"),
        ("organization_user", "Organization User"),
        ("developer", "Developer"),
    )

    # Add the role field
    role = models.CharField(
        max_length=20, choices=ROLE_CHOICES, default="organization_user"
    )

    # Add the organization field
    organization = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )

    temp_field = models.CharField(
        max_length=10, blank=True, null=True
    )  # Temporary field

    def __str__(self):
        return self.username
