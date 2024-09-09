from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from npoapi.models import Organization
from django.contrib.auth import authenticate
from npoapi.serializers import UserSerializer, OrganizationSerializer



# ViewSet for managing User registration and login
class UserViewSet(viewsets.ViewSet):
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    # Custom action for registering a new superuser
    @action(detail=False, methods=["post"], url_path="register")
    def register_account(self, request):
        user_serializer = UserSerializer(data=request.data)
        if user_serializer.is_valid():
            user = User.objects.create_user(
                username=user_serializer.validated_data["username"],
                first_name=user_serializer.validated_data["first_name"],
                last_name=user_serializer.validated_data["last_name"],
                password=user_serializer.validated_data["password"],
            )
            # Make the new user a superuser and staff
            #user.is_superuser = True
            #user.is_staff = True
            user.save()
            data = {**request.data, "user": user.id}
            org_serializer = OrganizationSerializer(data=data)
            if org_serializer.is_valid():
                Organization.objects.create(
                    user=org_serializer.validated_data["user"],
                    website=org_serializer.validated_data["website"],
                    name=org_serializer.validated_data["name"],
                    city=org_serializer.validated_data["city"],
                    state=org_serializer.validated_data["state"],
                    address=org_serializer.validated_data["address"]
                )
            else:
                print(org_serializer.errors)
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_201_CREATED)
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # Custom action for user login
    @action(detail=False, methods=["post"], url_path="login")
    def user_login(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)

        if user:
            token, created = Token.objects.get_or_create(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        else:
            return Response(
                {"error": "Invalid Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )

    # Custom action for user logout - - Not sure we want to handle logging out here, and if we should delete auth tokens
    @action(
        detail=False,
        methods=["post"],
        url_path="logout",
        permission_classes=[permissions.IsAuthenticated],
    )
    def user_logout(self, request):
        try:
            # Retrieve the token from the request header and delete it
            token = Token.objects.get(user=request.user)
            token.delete()
            return Response(
                {"message": "Logged out successfully."}, status=status.HTTP_200_OK
            )
        except Token.DoesNotExist:
            return Response(
                {"error": "Invalid request, token not found."},
                status=status.HTTP_400_BAD_REQUEST,
            )
