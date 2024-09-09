from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import serializers, status
from models.organization import Organization

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['user', 'website', 'name', 'city', 'state', 'address']


class OrganizationView(ViewSet):

    def create(self, request):
        """Handle POST operations for organization"""

        