import requests
from django.conf import settings  # Import settings to access GITHUB_INSTALLATION_ID


class GitHubService:
    def __init__(self, token, is_jwt=False):
        """
        token: The token to use (JWT or Installation Token).
        is_jwt: If true, indicates that the token is a JWT. Otherwise, it’s an installation token.
        """
        self.token = token
        self.is_jwt = is_jwt
        self.api_base_url = "https://api.github.com"

    def check_github_app_permissions(self):
        """
        Check the GitHub App's installation permissions using the JWT.
        """
        if not self.is_jwt:
            print("Error: A JWT is required to check GitHub App permissions.")
            return None

        url = f"{self.api_base_url}/app/installations/{settings.GITHUB_INSTALLATION_ID}"
        headers = {
            "Authorization": f"Bearer {self.token}",  # Use the JWT here
            "Accept": "application/vnd.github.v3+json",
        }

        print(f"Checking GitHub App permissions with URL: {url}")
        print(f"Headers: {headers}")

        response = requests.get(url, headers=headers)

        print(f"GitHub API Status Code (Permissions Check): {response.status_code}")
        print(f"GitHub API Response (Permissions Check): {response.text}")

        if response.status_code == 200:
            return response.json()
        else:
            print(
                f"Failed to retrieve app permissions: {response.status_code}, {response.text}"
            )
            return None

    def create_github_repo(self, name, description):
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        data = {
            "name": name,
            "description": description,
            "private": False,
        }

        # Ensure we're creating the repo under the correct organization 'nss-npo'
        response = requests.post(
            f"{self.api_base_url}/orgs/nss-npo/repos",  # Using the target org 'nss-npo'
            json=data,
            headers=headers,
        )

        if response.status_code == 201:  # Success
            return response.json().get("html_url")
        else:
            print(f"Failed to create repo: {response.status_code}, {response.text}")
            return None

    def check_if_repo_exists(self, name):
        """
        Check if a repository with the given name already exists.
        """
        headers = {
            "Authorization": f"Bearer {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        url = f"{self.api_base_url}/repos/nss-npo/{name}"

        print(f"Checking if repo {name} exists with URL: {url}")

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            print(f"Repo {name} exists.")
            return response.json().get("html_url")
        else:
            print(f"Repo {name} does not exist. Status Code: {response.status_code}")
            return None
