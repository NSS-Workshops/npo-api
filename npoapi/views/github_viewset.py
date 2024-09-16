from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.conf import settings
from django.contrib.auth import login as auth_login, get_user_model
from requests_oauthlib import OAuth2Session

User = get_user_model()


def github_login(request):
    """Redirects to GitHub for authentication."""
    print("GitHub login requested")

    # GitHub OAuth setup
    oauth = OAuth2Session(
        settings.GITHUB_CLIENT_ID,
        redirect_uri=settings.GITHUB_REDIRECT_URI,
        scope=["user:email"],
    )
    authorization_url, state = oauth.authorization_url(
        "https://github.com/login/oauth/authorize"
    )

    print("Authorization URL:", authorization_url)
    print("State:", state)

    request.session["oauth_state"] = state
    return redirect(authorization_url)


def github_callback(request):
    """Handles the GitHub callback and logs in the user."""
    print("GitHub callback received")

    state = request.GET.get("state")
    code = request.GET.get("code")
    print("Callback code:", code)
    print("Callback state:", state)

    if not state or not code:
        return HttpResponse("Missing state or code", status=400)

    # Check if state matches
    session_state = request.session.get("oauth_state")
    if state != session_state:
        print("State mismatch")
        return HttpResponse("Invalid state", status=400)

    # GitHub OAuth setup
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

    print("Token response:", token_response)

    # Fetch user info
    user_info_url = "https://api.github.com/user"
    oauth = OAuth2Session(settings.GITHUB_CLIENT_ID, token=token_response)
    user_info = oauth.get(user_info_url).json()

    print("User info:", user_info)

    # Find or create the user
    user, created = User.objects.get_or_create(
        username=user_info["login"],
        defaults={
            "email": user_info.get("email", ""),
            "first_name": user_info.get("name", ""),
            # Add additional fields if needed
        },
    )

    if created:
        print("User created:", user.username)
    else:
        print("User found:", user.username)

    # Log the user in
    auth_login(request, user)

    # Redirect to the home page or another page after successful login
    return redirect(reverse("home"))  # Adjust the URL name as needed
