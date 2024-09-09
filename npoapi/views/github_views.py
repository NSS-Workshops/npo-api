# npoapi/views/github_views.py

from django.shortcuts import redirect, render
from django.http import HttpResponse, JsonResponse  # Import JsonResponse
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required  # Import login_required
import requests
import urllib.parse
import secrets  # For secure state generation


# Step 1: Redirect to GitHub for authorization
def github_login(request):
    client_id = settings.GITHUB_CLIENT_ID
    redirect_uri = settings.GITHUB_REDIRECT_URI
    scope = "read:user user:email"

    # Generate a secure random string for CSRF protection
    state = secrets.token_urlsafe(16)
    request.session["oauth_state"] = state  # Store state in the user's session

    # Construct the GitHub authorization URL
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "scope": scope,
        "state": state,
    }
    url = "https://github.com/login/oauth/authorize?" + urllib.parse.urlencode(params)
    return redirect(url)


# Step 2: Handle the callback from GitHub

# npoapi/views/github_views.py

from django.http import JsonResponse


def github_callback(request):
    code = request.GET.get("code")
    state = request.GET.get("state")

    # Debugging output
    print(f"Received code: {code}")
    print(f"Received state: {state}")
    print(f"Session state: {request.session.get('oauth_state')}")

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

        # Check if a user with this GitHub username already exists
        try:
            user = User.objects.get(username=user_data["login"])
        except User.DoesNotExist:
            # If not, create a new user
            user = User.objects.create_user(
                username=user_data["login"],
                email=user_data.get("email", None),
                password=None,
            )

        # Log the user in
        login(request, user)

        # Create a response and set a secure, HTTP-only cookie with the access token
        response = redirect(
            f"http://localhost:3000/dashboard?username={user.username}&email={user.email}"
        )
        response.set_cookie(
            key="github_access_token",
            value=access_token,
            httponly=True,  # Makes the cookie inaccessible to JavaScript
            secure=False,  # Set to True in production when using HTTPS
            samesite="Lax",  # Prevents CSRF, but allows requests from same site
        )

        return response
    else:
        return HttpResponse("Error retrieving access token.", status=400)


# Add this new function to provide user information
@login_required
def user_info(request):
    user = request.user
    return JsonResponse({"username": user.username, "email": user.email})


@login_required
def fetch_repos(request):
    # Read the GitHub access token from the secure cookie
    access_token = request.COOKIES.get("github_access_token")

    if not access_token:
        return JsonResponse({"error": "Access token not found"}, status=403)

    # Use the access token to interact with the GitHub API
    response = requests.get(
        "https://api.github.com/user/repos",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code != 200:
        return JsonResponse(
            {"error": "Failed to fetch repositories"}, status=response.status_code
        )

    # Return the list of repositories to the frontend
    return JsonResponse(response.json(), safe=False)
