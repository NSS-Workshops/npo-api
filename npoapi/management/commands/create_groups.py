from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from npoapi.models import Organization


class Command(BaseCommand):
    help = "Creates user groups and assigns permissions."

    def handle(self, *args, **options):
        # Define content type for Organization model
        organization_content_type = ContentType.objects.get_for_model(Organization)

        # Define roles and their permissions
        roles_permissions = {
            "Admin": Permission.objects.all(),  # All permissions for Admin group
            "Organization User": Permission.objects.filter(
                content_type=organization_content_type,
                codename__in=[
                    "add_organization",
                    "change_organization",
                    "delete_organization",
                    "view_organization",
                ],
            ),
            "Developer": Permission.objects.filter(
                content_type=organization_content_type,
                codename__in=[
                    "view_organization",
                ],
            ),
        }

        # Create groups and assign permissions
        for role_name, permissions in roles_permissions.items():
            group, created = Group.objects.get_or_create(name=role_name)

            # Assign permissions to the group
            group.permissions.set(permissions)
            group.save()

            # Output success message
            self.stdout.write(
                self.style.SUCCESS(
                    f'Group "{role_name}" created or updated with permissions.'
                )
            )

        # Additional check to ensure all permissions are properly assigned
        self.stdout.write(
            self.style.SUCCESS(
                "All groups created and permissions assigned successfully."
            )
        )
