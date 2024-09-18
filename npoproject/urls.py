from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from npoapi.views import UserViewSet, OrganizationViewSet
from npoapi.views.github_viewset import github_login, github_callback
from npoapi.views.home_view import home  # Import the home view

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"organizations", OrganizationViewSet, basename="organization")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    path("github/login/", github_login, name="github_login"),
    path("github/callback/", github_callback, name="github_callback"),
    path("home/", home, name="home"),  # Add this line
]
