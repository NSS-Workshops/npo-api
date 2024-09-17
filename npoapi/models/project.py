from django.db import models
from .organization import Organization
from django.contrib.auth.models import Group


class Project(models.Model):
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    repository_url = models.URLField()
    description = models.TextField()

    def __str__(self):
        return self.description
