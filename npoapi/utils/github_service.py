# npoapi/utils/github_service.py

import requests


class GitHubService:
    def __init__(self, token):
        self.token = token
        self.api_base_url = "https://api.github.com"

    def create_github_repo(self, name, description):
        headers = {"Authorization": f"token {self.token}"}
        data = {
            "name": name,
            "description": description,
            "private": False,  # Adjust based on your needs
        }

        response = requests.post(
            f"{self.api_base_url}/orgs/nss-npo/repos",  # Use organization endpoint
            json=data,
            headers=headers,
        )

        if response.status_code == 201:  # Success
            return response.json().get("html_url")
        else:
            return None

    def check_if_repo_exists(self, name):
        headers = {"Authorization": f"token {self.token}"}
        url = f"{self.api_base_url}/repos/nss-npo/{name}"

        response = requests.get(url, headers=headers)
        if response.status_code == 200:  # Repo exists
            return response.json().get("html_url")
        else:
            return None
