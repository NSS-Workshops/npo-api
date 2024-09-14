# npoapi/views/github_auth.py

from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth import login
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
import requests
import urllib.parse
import secrets
from ..models import CustomUser  # Import your CustomUser model
from rest_framework.authtoken.models import Token  # Import DRF Token

# Step 1: Redirect to GitHub for authorization (github_login view remains the same)


# Step 2: Handle the callback from GitHub
@api_view(["GET"])
@permission_classes([AllowAny])
def github_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    # Verify the state parameter to prevent CSRF attacks
    if state != request.session.get("oauth_state"):
        return HttpResponse(
            "Invalid state parameter. Possible CSRF attack.", status=400
        )

    if code is None:
        return HttpResponse("Authorization failed. No code provided.", status=400)

    # Exchange the authorization code for an access token
    response = requests.post(
        "https://github.com/login/oauth/access_token",
        headers={"Accept": "application/json"},
        data={
            "client_id": settings.GITHUB_CLIENT_ID,
            "client_secret": settings.GITHUB_CLIENT_SECRET,
            "code": code,
            "redirect_uri": settings.GITHUB_REDIRECT_URI,
            "state": state,
        },
    )

    if response.status_code != 200:
        return HttpResponse("Failed to retrieve access token.", status=400)

    access_token = response.json().get("access_token")

    if access_token:
        # Use the access token to fetch user information
        user_response = requests.get(
            "https://api.github.com/user",
            headers={"Authorization": f"Bearer {access_token}"},
        )

        if user_response.status_code != 200:
            return HttpResponse(
                "Failed to fetch user information from GitHub.", status=400
            )

        user_data = user_response.json()

        # Extract user details from GitHub response
        username = user_data.get("login")
        email = user_data.get("email")
        full_name = user_data.get("name", "").split()
        first_name = full_name[0] if len(full_name) > 0 else ""
        last_name = full_name[1] if len(full_name) > 1 else ""

        # Check if a user with this GitHub username already exists
        try:
            user = CustomUser.objects.get(username=username)
        except CustomUser.DoesNotExist:
            # If not, create a new user with role 'developer'
            user = CustomUser.objects.create_user(
                username=username,
                email=email,
                first_name=first_name,
                last_name=last_name,
                password=None,  # No password is set for OAuth-authenticated users
                role="developer",
            )

        # Log the user in
        login(request, user)

        # Create or get a DRF token for the user
        token, created = Token.objects.get_or_create(user=user)

        # Return the token in the response
        response_data = {
            "token": token.key,
            "username": user.username,
            "email": user.email,
        }
        return JsonResponse(response_data)
    else:
        return HttpResponse("Error retrieving access token.", status=400)
