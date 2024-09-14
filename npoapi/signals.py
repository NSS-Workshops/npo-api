# npoapi/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import Permission
from .models import CustomUser


@receiver(post_save, sender=CustomUser)
def assign_user_permissions(sender, instance, created, **kwargs):
    if created:
        if instance.role == "admin":
            # Assign all permissions
            permissions = Permission.objects.all()
        elif instance.role == "organization_user":
            # Assign specific permissions
            permissions = Permission.objects.filter(
                codename__in=[
                    "can_manage_organization",
                    "can_manage_repositories",
                    "can_manage_users",
                    "can_contribute_to_repositories",
                ]
            )
        elif instance.role == "developer":
            # Assign specific permission
            permissions = Permission.objects.filter(
                codename="can_contribute_to_repositories"
            )
        instance.user_permissions.set(permissions)
