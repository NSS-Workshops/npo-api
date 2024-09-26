import jwt
import time
import requests
from django.conf import settings


class GitHubTokenService:
    def __init__(self):
        self.api_base_url = "https://api.github.com"
        self.github_app_id = settings.GITHUB_APP_ID
        self.github_private_key = settings.GITHUB_PRIVATE_KEY.replace("\\n", "\n")
        self.github_installation_id = settings.GITHUB_INSTALLATION_ID

    def generate_jwt(self):
        """Generate a JWT to authenticate the GitHub App"""
        payload = {
            "iat": int(time.time()),  # Issued at time
            "exp": int(time.time()) + (5 * 60),  # Expires after 5 minutes
            "iss": self.github_app_id,  # GitHub App ID
        }

        try:
            # Debugging: Show the payload
            print(f"JWT Payload: {payload}")

            # Debugging: Show the first part of the private key (for security reasons, only show part of it)
            # print(f"Private Key (truncated): {self.github_private_key[:50]}...")

            # Generate the JWT
            jwt_token = jwt.encode(payload, self.github_private_key, algorithm="RS256")

            # Debugging: Print the generated JWT
            print(f"Generated JWT: {jwt_token}")

            return jwt_token

        except Exception as e:
            # Debugging: Print error if JWT generation fails
            print(f"Error generating JWT: {e}")
            return None

    def get_installation_token(self):
        """Generate the installation access token from GitHub"""
        jwt_token = self.generate_jwt()

        if not jwt_token:
            print("JWT generation failed.")
            return None

        headers = {
            "Authorization": f"Bearer {jwt_token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{self.api_base_url}/app/installations/{self.github_installation_id}/access_tokens"

        try:
            # Debugging: Print the request details
            print(f"Requesting installation token with JWT: {jwt_token}")
            print(f"Request Headers: {headers}")
            print(f"Request URL: {url}")

            response = requests.post(url, headers=headers)

            # Debugging: Print the status code and response
            print(f"GitHub API Status Code: {response.status_code}")
            print(f"GitHub API Response: {response.text}")

            if response.status_code == 201:
                return response.json().get("token")
            else:
                print(f"Failed to retrieve installation token: {response.status_code}")
                return None

        except requests.RequestException as e:
            # Debugging: Catch and log any request-related exceptions
            print(f"Error fetching installation token: {e}")
            return None
