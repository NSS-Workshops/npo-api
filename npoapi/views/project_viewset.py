from rest_framework import viewsets, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth.models import Group
from npoapi.models import Project
from npoapi.serializers import ProjectSerializer
from npoapi.utils import GitHubService
from django.views.decorators.csrf import csrf_exempt
import re
from datetime import datetime


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        # Step 1: Validate and serialize the incoming data
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        # Step 2: Extract name and description from validated data
        project_data = serializer.validated_data
        repo_name = project_data["name"]  # Extract project name
        description = project_data["description"]  # Extract project description

        # Step 3: Get the OAuth token from cookies
        github_token = request.COOKIES.get("oauth_token")
        if not github_token:
            return Response(
                {"error": "No OAuth token found in cookies."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Step 4: Check if repository already exists (optional but helpful)
        github_service = GitHubService(token=github_token)
        existing_repo_url = github_service.check_if_repo_exists(repo_name)
        if existing_repo_url:
            return Response(
                {"error": "Repository already exists on GitHub."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 5: Create the GitHub repository
        repo_url = github_service.create_github_repo(
            name=repo_name, description=description
        )

        if not repo_url:
            return Response(
                {"error": "Failed to create the GitHub repository."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 6: Save the project to the database, including the repo URL
        project = Project.objects.create(
            organization=project_data["organization"],
            name=repo_name,
            description=description,
            repository_url=repo_url,  # GitHub repo URL is saved here
        )

        # Step 7: Return the created project in the response
        response_serializer = ProjectSerializer(project)
        return Response(
            {
                "message": "Project created and GitHub repository created.",
                "project": response_serializer.data,
                "github_repo": repo_url,
            },
            status=status.HTTP_201_CREATED,
        )
