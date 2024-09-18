from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import Organization  # Import the Organization model

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "groups",  # Include the groups field for assigning roles
        ]
        extra_kwargs = {
            "password": {"write_only": True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        groups_data = validated_data.pop("groups", [])  # Handle groups separately
        user = User(**validated_data)
        user.set_password(validated_data.pop("password"))  # Hash password
        user.save()
        user.groups.set(groups_data)  # Assign groups
        return user

    def update(self, instance, validated_data):
        groups_data = validated_data.pop("groups", None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if "password" in validated_data:
            instance.set_password(validated_data["password"])  # Hash password
        instance.save()

        if groups_data is not None:
            instance.groups.set(groups_data)  # Update groups
        return instance


class OrganizationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Organization User"),
        required=False,
    )

    class Meta:
        model = Organization
        fields = ["id", "name", "website", "address", "city", "state", "user"]
