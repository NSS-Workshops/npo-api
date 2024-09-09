from rest_framework import serializers
from django.contrib.auth.models import User
from npoapi.models.organization import Organization

# Serializer for the User model
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "password", "first_name", "last_name"]
        extra_kwargs = {
            "password": {"write_only": True}
        }  # Ensure password is write-only


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['user', 'website', 'name', 'city', 'state', 'address']
