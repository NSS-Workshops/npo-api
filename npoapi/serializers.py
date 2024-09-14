from rest_framework import serializers
from django.contrib.auth.models import Group
from django.contrib.auth import (
    get_user_model,
)  # Import get_user_model to dynamically reference the user model
from .models import Organization

# Use get_user_model() to get the custom user model dynamically
User = get_user_model()


class CustomUserSerializer(serializers.ModelSerializer):
    groups = serializers.SlugRelatedField(
        many=True,
        slug_field="name",
        queryset=Group.objects.all(),
        required=False,
        allow_null=True,
        error_messages={
            "does_not_exist": 'Group "{value}" does not exist.',
            "invalid": "Invalid group name. Expected a string representing the group name.",
        },
    )

    class Meta:
        model = User  # Use the dynamically obtained user model
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "groups",
            "organization",
            "password",
        ]
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def create(self, validated_data):
        # Handle password hashing
        password = validated_data.pop("password", None)
        groups = validated_data.pop("groups", None)

        # Create user instance
        user = User(**validated_data)

        if password:
            user.set_password(password)  # Hash the password
        user.save()

        # Add user to groups
        if groups:
            # Convert group names to Group instances
            group_instances = Group.objects.filter(name__in=groups)
            user.groups.set(group_instances)

        return user


class OrganizationSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.filter(groups__name="Organization User"),
        required=False,
    )

    class Meta:
        model = Organization
        fields = ["id", "name", "website", "address", "city", "state", "user"]
