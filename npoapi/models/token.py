from django.conf import settings
from django.db import models
from rest_framework.authtoken.models import Token as DefaultToken


class Token(DefaultToken):
    # Do not redefine the 'user' field here as it already exists in the base class
    class Meta:
        proxy = True  # This is a proxy model for the default Token model
