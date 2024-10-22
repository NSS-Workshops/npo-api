from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from npoapi.models import Project, Organization
from npoapi.serializers import ProjectSerializer
from npoapi.services.github_token_service import GitHubTokenService
from npoapi.services.github_service import GitHubService


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    queryset = (
        Project.objects.all()
    )  # Default queryset for global listing (developer view)

    # Custom action to get projects for the user's organization
    @action(
        detail=False,
        methods=["get"],
        url_path="user-projects",
        permission_classes=[IsAuthenticated],
    )
    def get_user_projects(self, request):
        user = request.user
        try:
            # Fetch the organization linked to the authenticated user
            organization = Organization.objects.get(user=user)

            # Retrieve the projects for this organization
            projects = Project.objects.filter(organization=organization)

            if not projects:
                return Response(
                    {"detail": "No projects found for this organization."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            serializer = ProjectSerializer(projects, many=True)
            return Response({"projects": serializer.data}, status=status.HTTP_200_OK)

        except Organization.DoesNotExist:
            return Response(
                {"detail": "No organization found for the user."},
                status=status.HTTP_404_NOT_FOUND,
            )

    # --------------------------------
    # CREATE: /projects/
    # --------------------------------
    def create(self, request, *args, **kwargs):
        print("Received request to create project")

        # Step 1: Validate and serialize the incoming data
        serializer = self.get_serializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        print("Data is valid")

        # Extract project data
        project_data = serializer.validated_data
        repo_name = project_data["name"]
        description = project_data["description"]

        # Step 2: Initialize GitHubTokenService
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


def retrieve(self, request, *args, **kwargs):
    """
    Retrieve a specific project by its ID, ensuring the user has permission to view it.
    """
    print("Received request to retrieve project")

    # Step 1: Get the project object by ID
    project = (
        self.get_object()
    )  # This fetches the project by its ID using the DRF's default behavior.
    print(f"Found project with ID {project.id}")

    # Step 2: Check if the user has permission to view the project
    if (
        project.organization.owner != request.user
    ):  # Assuming `organization.owner` defines ownership
        print(f"User {request.user} does not have permission to view this project.")
        raise PermissionDenied("You do not have permission to view this project.")

    # Step 3: Serialize the project data
    serializer = self.get_serializer(project)

    # Step 4: Return the serialized project data in the response
    return Response(
        {
            "message": "Project retrieved successfully.",
            "project": serializer.data,
        },
        status=status.HTTP_200_OK,
    )

    # --------------------------------
    # UPDATE: /projects/<id>/
    # --------------------------------
    def update(self, request, *args, **kwargs):
        """
        Update an existing project by its ID.
        """
        print("Received request to update project")

        # Step 1: Get the project object
        project = self.get_object()  # This method fetches the project by ID
        print(f"Found project with ID {project.id}")

        # Step 2: Validate and serialize the incoming data
        serializer = self.get_serializer(project, data=request.data, partial=False)
        serializer.is_valid(raise_exception=True)
        print("Data is valid")

        # Step 3: Save the updated project data
        self.perform_update(serializer)
        print(f"Project with ID {project.id} updated successfully")

        # Step 4: Return the updated project data in the response
        return Response(
            {
                "message": "Project updated successfully.",
                "project": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # --------------------------------
    # PARTIAL UPDATE: /projects/<id>/ (PATCH method)
    # --------------------------------
    def partial_update(self, request, *args, **kwargs):
        """
        Partially update an existing project by its ID.
        """
        print("Received request to partially update project")

        # Step 1: Get the project object
        project = self.get_object()  # This method fetches the project by ID
        print(f"Found project with ID {project.id}")

        # Step 2: Validate and serialize the incoming data (partial=True allows partial updates)
        serializer = self.get_serializer(project, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        print("Partial data is valid")

        # Step 3: Save the partially updated project data
        self.perform_update(serializer)
        print(f"Project with ID {project.id} partially updated successfully")

        # Step 4: Return the partially updated project data in the response
        return Response(
            {
                "message": "Project partially updated successfully.",
                "project": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    # --------------------------------
    # DELETE: /projects/<id>/
    # --------------------------------
    def destroy(self, request, *args, **kwargs):
        """
        Delete an existing project by its ID.
        """
        print("Received request to delete project")

        # Step 1: Get the project object
        project = self.get_object()  # This method fetches the project by ID
        print(f"Found project with ID {project.id}")

        # Step 2: Delete the project from the database
        project.delete()
        print(f"Project with ID {project.id} deleted successfully")

        # Step 3: Return a success response
        return Response(
            {
                "message": "Project deleted successfully.",
            },
            status=status.HTTP_204_NO_CONTENT,
        )

    # --------------------------------
    # LIST: /projects/ (Global list for developers)
    # --------------------------------
    def list(self, request, *args, **kwargs):
        """
        List all projects (global view, e.g., for developers).
        """
        print("Received request to list all projects")

        # Step 1: Get all projects
        projects = self.get_queryset()
        print(f"Found {projects.count()} projects")

        # Step 2: Serialize the projects
        serializer = self.get_serializer(projects, many=True)

        # Step 3: Return the serialized projects in the response
        return Response(
            {
                "message": "Projects retrieved successfully.",
                "projects": serializer.data,
            },
            status=status.HTTP_200_OK,
        )
