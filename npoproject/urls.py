# npoapi/urls.py

from django.urls import include, path
from rest_framework import routers
from npoapi.views.user_view import UserViewSet
from npoapi.views.github_views import (
    github_login,
    github_callback,
    user_info,
    fetch_repos,
)

router = routers.DefaultRouter(trailing_slash=False)  # No trailing slash

router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
    path("github/login/", github_login, name="github_login"),  # No trailing slash
    path(
        "github/callback", github_callback, name="github_callback"
    ),  # No trailing slash
    path("api/user-info", user_info, name="user-info"),  # No trailing slash
    path("api/fetch-repos", fetch_repos, name="fetch_repos"),
]
