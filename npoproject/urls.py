from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from npoapi.views.user_view import UserViewSet  # Import from views package

router = routers.DefaultRouter(trailing_slash=False)
router.register(r"users", UserViewSet, basename="user")

urlpatterns = [
    path("", include(router.urls)),
]
