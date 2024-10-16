from datetime import timedelta
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

        # Automatically log in the user after registration
        login(request, user)

        # Return the created user's information
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
        Endpoint to log in a user and return user info along with an authentication token in cookies.
        URL: /users/login/
        Method: POST
        Request Body:
        {
            "username": "your_username",
            "password": "your_password"
        }
        Response:
        {
            "message": "Logged in successfully.",
            "user": {
                "username": "johndoe",
                "email": "johndoe@example.com",
                "first_name": "John",
                "last_name": "Doe",
                "group": "Developer"  # Assuming group is represented like this
            },
            "auth_token": "your_auth_token"
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

            # Serialize the user data
            user_data = UserSerializer(user).data

            # Set the token in an HTTP-only cookie
            response = Response(
                {
                    "message": "Logged in successfully.",
                    "user": user_data,  # Send user data in the response
                    "auth_token": token.key,  # Also include token for client-side storage if necessary
                },
                status=status.HTTP_200_OK,
            )
            response.set_cookie(
                "auth_token",
                token.key,
                max_age=timedelta(days=30),  # Cookie expiration time
                httponly=True,  # Prevent JavaScript access
                secure=False,  # Set to True for production with HTTPS
            )
            return response
        else:
            return Response(
                {"error": "Invalid credentials."},
                status=status.HTTP_400_BAD_REQUEST,
            )

    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[permissions.IsAuthenticated],
    )
    def user_logout(self, request):
        """
        Log out the user and remove the auth token cookie.
        """
        response = Response(
            {"message": "Logged out successfully."}, status=status.HTTP_200_OK
        )
        response.delete_cookie("auth_token")
        return response

    # Fix indentation here for retrieve method
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
        instance = self.get_object()  # Get the user instance
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )  # Use correct method to get serializer

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        self.perform_update(serializer)  # Perform the update

        return Response(serializer.data, status=status.HTTP_200_OK)
