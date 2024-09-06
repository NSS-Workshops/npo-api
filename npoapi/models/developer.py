from django.db import models
from django.contrib.auth.models import User

class Developer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    github_profile = models.URLField()

    def __str__(self):
        return self.user.username