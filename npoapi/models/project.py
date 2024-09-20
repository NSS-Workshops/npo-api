from django.db import models
from .organization import Organization
from django.contrib.auth.models import Group


class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(
        max_length=255, default="Unnamed Project"
    )  # Add default here
    repository_url = models.URLField(null=True, blank=True)  # Allow it to be null/blank
    description = models.TextField()

    def __str__(self):
        return self.description
