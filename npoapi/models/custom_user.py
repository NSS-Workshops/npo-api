# models.py
from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    # Remove the 'role' field
    # Use groups to define roles instead

    organization = models.ForeignKey(
        "Organization", null=True, blank=True, on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.username
