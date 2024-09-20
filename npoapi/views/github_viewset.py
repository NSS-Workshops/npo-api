from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import login as auth_login, get_user_model
from requests_oauthlib import OAuth2Session
from datetime import timedelta

User = get_user_model()


def github_login(request):
    """Redirects to GitHub for authentication."""
    oauth = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        redirect_uri=settings.GITHUB_REDIRECT_URI,
        scope=["repo", "user"],
    )
    authorization_url, state = oauth.authorization_url(
        "https://github.com/login/oauth/authorize"
    )
    request.session["oauth_state"] = state
    return redirect(authorization_url)


def github_callback(request):
    """Handles the GitHub callback and logs in the user."""
    state = request.GET.get("state")
    code = request.GET.get("code")

    if not state or not code:
        return HttpResponse("Missing state or code", status=400)

    session_state = request.session.get("oauth_state")
    if state != session_state:
        return HttpResponse("Invalid state", status=400)

    oauth = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        redirect_uri=settings.GITHUB_REDIRECT_URI,
        state=state,
    )
    token_url = "https://github.com/login/oauth/access_token"
    token_response = oauth.fetch_token(
        token_url,
        client_secret=settings.GITHUB_CLIENT_SECRET,
        code=code,
        include_client_id=True,
    )

    print("Token Response:", token_response)  # <-- Debugging: Print the token

    # Fetch user info
    user_info_url = "https://api.github.com/user"
    oauth = OAuth2Session(settings.GITHUB_CLIENT_ID, token=token_response)
    user_info = oauth.get(user_info_url).json()

    # Find or create the user
    user, created = User.objects.get_or_create(
        username=user_info["login"],
        defaults={
            "email": user_info.get("email", ""),
            "first_name": user_info.get("name", ""),
        },
    )

    # Log the user in
    auth_login(request, user)

    response = redirect(reverse("home"))  # Adjust the URL name as needed
    response.set_cookie(
        "oauth_token",
        token_response["access_token"],
        max_age=timedelta(days=30),  # Cookie expiration time
        httponly=True,  # Prevent access via JavaScript
        secure=False,  # Use True for HTTPS, False for local development (adjust as necessary)
    )
    print("OAuth token set in cookie:", response.cookies.get("oauth_token"))

    return response  # Ensure this is inside the function


"""
from requests_oauthlib import OAuth2Session

def some_view(request):
    # Retrieve the OAuth token from the cookie
    oauth_token = request.COOKIES.get('oauth_token')

    if not oauth_token:
        return HttpResponse("OAuth token not found", status=403)

    # Use the token to make API calls to GitHub
    oauth = OAuth2Session(settings.GITHUB_CLIENT_ID, token={'access_token': oauth_token})
    user_repos_url = "https://api.github.com/user/repos"
    response = oauth.get(user_repos_url)

    if response.status_code != 200:
        return HttpResponse(f"GitHub API call failed: {response.text}", status=response.status_code)

    # Do something with the API response
    user_repos = response.json()
    return HttpResponse(user_repos)
    """
