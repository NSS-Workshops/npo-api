from rest_framework.viewsets import ModelViewSet  # Import ModelViewSet correctly
from rest_framework import status
from rest_framework.response import Response
from ..models import Organization  # Correct relative import for the Organization model
from ..serializers import (
    OrganizationSerializer,
)  # Correct relative import for the serializer


class OrganizationViewSet(ModelViewSet):
    """
    A simple ViewSet for creating and managing Organizations.
    """

    def create(self, request):
        """Handle POST operations for creating an organization"""
        serializer = OrganizationSerializer(data=request.data)

        if serializer.is_valid():  # Validate the incoming data
            serializer.save()  # Save the new organization instance
            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )  # Respond with the created data and HTTP 201

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )  # Respond with validation errors and HTTP 400

    def list(self, request):
        """Handle GET requests for listing all organizations"""
        organizations = Organization.objects.all()
        serializer = OrganizationSerializer(organizations, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, pk=None):
        """Handle GET requests for retrieving a single organization"""
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrganizationSerializer(organization)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, pk=None):
        """Handle PUT requests for updating an organization"""
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrganizationSerializer(organization, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def destroy(self, request, pk=None):
        """Handle DELETE requests for deleting an organization"""
        try:
            organization = Organization.objects.get(pk=pk)
        except Organization.DoesNotExist:
            return Response(
                {"error": "Organization not found"}, status=status.HTTP_404_NOT_FOUND
            )

        organization.delete()
        return Response(
            {"message": "Organization deleted successfully"},
            status=status.HTTP_204_NO_CONTENT,
        )
