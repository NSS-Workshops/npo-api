from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate, login, get_user_model
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import Group
from npoapi.serializers import CustomUserSerializer

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):
        if self.action in ["list", "retrieve"]:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == "create":
            permission_classes = [permissions.AllowAny]
        elif self.action in ["update", "partial_update", "destroy"]:
            permission_classes = [permissions.IsAuthenticated]
        else:
            permission_classes = [permissions.AllowAny]
        return [permission() for permission in permission_classes]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Save the user
        self.perform_create(serializer)
        user = User.objects.get(username=serializer.data["username"])

        # Assign the correct group(s) based on the request data
        if "groups" in request.data:
            group_ids = request.data["groups"]  # Expecting a list of group IDs
            user.groups.set(
                group_ids
            )  # Correct way to assign many-to-many relationships

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
