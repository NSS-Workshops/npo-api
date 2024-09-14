from django.db import models
from .custom_user import CustomUser  # Import the CustomUser model


# Define an Organization model
class Organization(models.Model):
    name = models.CharField(max_length=100)
    website = models.URLField()
    address = models.TextField()
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    user = models.OneToOneField(
        CustomUser, on_delete=models.CASCADE, related_name="organization_user"
    )

    class Meta:
        permissions = [
            ("can_manage_organization", "Can manage organization details"),
            ("can_manage_repositories", "Can manage repositories"),
            ("can_manage_users", "Can manage users"),
            ("can_contribute_to_repositories", "Can contribute to repositories"),
        ]

    def __str__(self):
        return self.name
