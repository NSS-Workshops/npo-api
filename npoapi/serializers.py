from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import (
    get_user_model,
)  # Import get_user_model to dynamically reference the user model
from .models import Organization

# Get the custom user model
CustomUser = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    groups = serializers.PrimaryKeyRelatedField(
        queryset=Group.objects.all(), many=True
    )  # Expecting a list of group IDs

    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
            "organization",
            "groups",  # Include the groups field for assigning roles
        ]
        extra_kwargs = {
            "password": {"write_only": True},  # Ensure password is write-only
        }

    def create(self, validated_data):
        """
        Overriding the create method to handle password hashing and group assignment properly.
        """
        groups_data = validated_data.pop(
            "groups", []
        )  # Remove groups data from validated_data
        password = validated_data.pop(
            "password", None
        )  # Handle the password separately

        # Create the user instance
        user = CustomUser(**validated_data)
        if password:
            user.set_password(password)  # Hash the password before saving
        user.save()  # Save the user instance

        # Assign the groups
        user.groups.set(groups_data)  # Correct way to assign many-to-many relationships
        return user

    def update(self, instance, validated_data):
        """
        Overriding the update method to handle updating a user instance.
        """
        groups_data = validated_data.pop("groups", None)
        password = validated_data.pop("password", None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        if password:
            instance.set_password(password)  # Hash the password before saving
        instance.save()

        if groups_data is not None:
            instance.groups.set(
                groups_data
            )  # Correct way to update many-to-many relationships

        return instance


class OrganizationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(groups__name="Organization User"),
        required=False,
    )

    class Meta:
        model = Organization
        fields = ["id", "name", "website", "address", "city", "state", "user"]
