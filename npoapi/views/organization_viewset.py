# views/organization_viewset.py
from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from npoapi.models import Organization
from npoapi.serializers import OrganizationSerializer
from rest_framework.decorators import action


class OrganizationViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing, creating, updating, and deleting organizations.
    Permissions are managed based on Django's built-in group and permission system.
    """

    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [DjangoModelPermissions]  # Use Django's built-in permissions

    def get_permissions(self):
        """
        This method assigns permissions based on the action being performed.
        DjangoModelPermissions will check the user's group-based permissions.
        """
        # Assign different permission classes based on the action
        if self.action in ["list", "retrieve"]:
            # Allow any authenticated user to view organizations
            permission_classes = [DjangoModelPermissions]
        elif self.action in ["create", "update", "partial_update", "destroy"]:
            # Only allow users with specific permissions to create, update, or delete organizations
            permission_classes = [DjangoModelPermissions]
        else:
            permission_classes = [DjangoModelPermissions]
        return [permission() for permission in permission_classes]

    # Custom action to retrieve the organization associated with the logged-in user
    @action(
        detail=False,
        methods=["get"],
        url_path="user",
        permission_classes=[IsAuthenticated],
    )
    def get_user_organization(self, request):
        """
        Retrieves the organization associated with the logged-in user.
        """
        user = request.user
        try:
            # Assuming the organization is associated with the user via a ForeignKey
            organization = Organization.objects.get(user=user)
            serializer = OrganizationSerializer(organization)
            return Response(serializer.data)
        except Organization.DoesNotExist:
            return Response(
                {"detail": "No organization found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            )

    def create(self, request, *args, **kwargs):
        """
        Create a new organization if the user has the necessary permissions.
        """
        # Check if the user has permission to create an organization
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        """
        Update an existing organization if the user has the necessary permissions.
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response(serializer.data)

    def destroy(self, request, *args, **kwargs):
        """
        Delete an organization if the user has the necessary permissions.
        """
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def list(self, request, *args, **kwargs):
        """
        List all organizations if the user has the necessary permissions.
        """
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve a single organization if the user has the necessary permissions.
        """
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
