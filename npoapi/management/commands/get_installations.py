# npoapi/management/commands/get_installations.py

from django.core.management.base import BaseCommand
from django.conf import settings
import jwt
import time
import requests


class Command(BaseCommand):
    help = "Get GitHub App installation token"

    # Generate the JWT (valid for 10 minutes)
    def generate_jwt(self):
        payload = {
            "iat": int(time.time()),  # Issued at time
            "exp": int(time.time()) + (5 * 60),  # Expires after 5 minutes
            "iss": int(settings.GITHUB_APP_ID),  # GitHub App ID
        }

        return jwt.encode(payload, settings.GITHUB_PRIVATE_KEY, algorithm="RS256")

    # Generate the installation access token
    def get_installation_token(self):
        jwt_token = self.generate_jwt()
        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"https://api.github.com/app/installations/{settings.GITHUB_INSTALLATION_ID}/access_tokens"
        response = requests.post(url, headers=headers)

        if response.status_code == 201:
            token = response.json()["token"]
            self.stdout.write(f"Installation Token: {token}")
        else:
            self.stdout.write(f"Failed to retrieve token: {response.status_code}")
            self.stdout.write(str(response.json()))

    # Entry point for the management command
    def handle(self, *args, **kwargs):
        self.get_installation_token()
