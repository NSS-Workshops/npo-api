from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from npoapi.views import UserViewSet, OrganizationViewSet

router = routers.DefaultRouter()
router.register(r"users", UserViewSet, basename="user")
router.register(r"organizations", OrganizationViewSet, basename="organization")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(router.urls)),
    # ... other URL patterns ...
]
