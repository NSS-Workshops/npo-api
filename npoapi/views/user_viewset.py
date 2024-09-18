from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from npoapi.serializers import (
    UserSerializer,
)  # Ensure this serializer includes the organization field

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset that provides the standard actions for the User model,
    including CRUD functionality and custom login.
    """

    queryset = User.objects.all()
    serializer_class = (
        UserSerializer  # Ensure your UserSerializer includes 'organization'
    )

    def get_permissions(self):
        if self.action in ["list", "retrieve", "update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        """
        Endpoint to create a new user.
        URL: /users/
        Method: POST
        Request Body:
        {
            "username": "newuser",
            "email": "user@example.com",
            "password": "securepassword",
            "first_name": "First",
            "last_name": "Last",
            "organization": 1,  # Assuming you have an Organization with ID 1
            "groups": [2]  # Optional: IDs of the groups to assign
        }
        """
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save the user
        user = serializer.save()

        # Assign groups if provided
        if "groups" in request.data:
            group_ids = request.data["groups"]
            user.groups.set(group_ids)

        # Log the user in after registration
        login(request, user)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    @action(
        detail=False,
        methods=["post"],
        url_path="login",
        permission_classes=[permissions.AllowAny],
    )
    def user_login(self, request):
        """
        Endpoint to log in a user and return an authentication token.
        URL: /users/login/
        Method: POST
        Request Body:
        {
            "username": "your_username",
            "password": "your_password"
        }
        Response:
        {
            "token": "some_generated_token"
        }
        """
        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:
            return Response(
                {"error": "Username and password are required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Authenticate the user
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request, user)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    def retrieve(self, request, pk=None):
        """
        Endpoint to retrieve a specific user.
        URL: /users/<id>/
        Method: GET
        """
        try:
            user = User.objects.get(pk=pk)
            serializer = self.get_serializer(user)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )

    def update(self, request, *args, **kwargs):
        """
        Endpoint to update a specific user.
        URL: /users/<id>/
        Method: PUT
        """
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        """
        Endpoint to partially update a specific user.
        URL: /users/<id>/
        Method: PATCH
        """
        return self.update(request, *args, **kwargs, partial=True)

    def destroy(self, request, pk=None):
        """
        Endpoint to delete a specific user.
        URL: /users/<id>/
        Method: DELETE
        """
        try:
            user = User.objects.get(pk=pk)
            user.delete()
            return Response(
                {"success": "User deleted successfully."},
                status=status.HTTP_204_NO_CONTENT,
            )
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."}, status=status.HTTP_404_NOT_FOUND
            )
