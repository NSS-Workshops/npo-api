from rest_framework import viewsets, status
from rest_framework.response import Response
from npoapi.models import Project
from npoapi.serializers import ProjectSerializer
from npoapi.services.github_token_service import GitHubTokenService
from npoapi.services.github_service import GitHubService


class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def create(self, request, *args, **kwargs):
        print("Received request to create project")

        # Step 1: Validate and serialize the incoming data
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        print("Data is valid")

        # Extract name and description from validated data
        project_data = serializer.validated_data
        repo_name = project_data["name"]
        description = project_data["description"]

        # Step 2: Initialize the GitHubTokenService
        github_token_service = GitHubTokenService()

        # Step 3: Generate the JWT to check GitHub App permissions
        print("Generating JWT for permission check...")
        jwt_token = github_token_service.generate_jwt()

        # Step 4: Use the JWT to check GitHub App permissions
        github_service_jwt = GitHubService(token=jwt_token, is_jwt=True)
        permissions = github_service_jwt.check_github_app_permissions()

        if not permissions:
            print("GitHub App does not have the required permissions.")
            return Response(
                {
                    "error": "GitHub App does not have the required permissions to create repositories."
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        # Step 5: Get the installation token to create the repository
        print("Getting installation token for repo creation...")
        installation_token = github_token_service.get_installation_token()

        if not installation_token:
            return Response(
                {"error": "Unable to retrieve installation token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # Step 6: Use the installation token to create a GitHub repository
        github_service_installation = GitHubService(token=installation_token)
        repo_url = github_service_installation.create_github_repo(
            name=repo_name, description=description
        )

        if not repo_url:
            print("Failed to create GitHub repository.")
            return Response(
                {"error": "Failed to create the GitHub repository."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Step 7: Save the project to the database, including the repo URL
        project = Project.objects.create(
            organization=project_data["organization"],
            name=repo_name,
            description=description,
            repository_url=repo_url,
        )

        # Step 8: Return the created project in the response
        response_serializer = ProjectSerializer(project)
        return Response(
            {
                "message": "Project created and GitHub repository created.",
                "project": response_serializer.data,
                "github_repo": repo_url,
            },
            status=status.HTTP_201_CREATED,
        )
