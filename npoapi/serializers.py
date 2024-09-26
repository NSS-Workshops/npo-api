from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model
from .models import Organization, Project  # Import the Organization and Project models
from .services.github_service import (
    GitHubService,
)  # Import a utility for GitHub repo creation

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True, required=False
    )
    organization = serializers.PrimaryKeyRelatedField(
        queryset=Organization.objects.all(),
        required=False,  # Optional Organization field
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
            "groups",  # Group roles for the user
            "organization",  # Organization field
        ]
        extra_kwargs = {
            "password": {"write_only": True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        groups_data = validated_data.pop("groups", [])  # Handle groups separately
        organization = validated_data.pop(
            "organization", None
        )  # Handle organization separately
        user = User(**validated_data)
        user.set_password(validated_data.pop("password"))  # Hash password before saving
        user.save()

        user.groups.set(groups_data)  # Assign groups to the user
        if organization:
            user.organization = organization  # Assign organization if provided
            user.save()

        return user

    def update(self, instance, validated_data):
        groups_data = validated_data.pop("groups", None)
        organization = validated_data.pop("organization", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if "password" in validated_data:
            instance.set_password(
                validated_data["password"]
            )  # Hash password before updating
        instance.save()

        if groups_data is not None:
            instance.groups.set(groups_data)  # Update groups if provided

        if organization is not None:
            instance.organization = organization  # Update organization if provided
            instance.save()

        return instance


class OrganizationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Organization User"),
        required=False,
    )

    class Meta:
        model = Organization
        fields = ["id", "name", "website", "address", "city", "state", "user"]


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "organization", "name", "repository_url", "description"]
        read_only_fields = [
            "repository_url"
        ]  # Make repository_url read-only, as it's set after GitHub repo creation

    def create(self, validated_data):
        # Create the Project instance
        return Project.objects.create(**validated_data)
