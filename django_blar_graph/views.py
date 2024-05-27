from django.contrib.auth.models import Group, User
from rest_framework import generics, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from django_blar_graph.models import Repos
from django_blar_graph.serializers import (
    CloneRepoSerializer,
    GroupSerializer,
    ReposSerializer,
    RetrieveReposSerializer,
    UserSerializer,
)
from django_blar_graph.services.git_hub import (
    clone_repo_from_github,
    get_repository_from_db,
)

from .serializers import RegisterSerializer


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all().order_by('name')
    serializer_class = GroupSerializer
    permission_classes = [IsAuthenticated]
    

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class CloneRepoView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        user = request.user  # Extract user from request
        serializer = CloneRepoSerializer(data=request.data)
        if serializer.is_valid():
            repo_id = serializer.validated_data.get('repo_id')            
            repository = get_repository_from_db(repo_id, user)
            if repository:
                branch = serializer.validated_data.get('branch', repository.main_branch)
                result = clone_repo_from_github(repository, branch)
                if result:
                    return Response({'message': 'Repository cloned successfully'}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Failed to clone repository'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            else:
                return Response({'error': 'Repository not found'}, status=status.HTTP_404_NOT_FOUND)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class CreateRepoView(APIView):
    authentication_classes = [JWTAuthentication]  # Use JWT authentication
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        serializer = ReposSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            repo = serializer.save()
            return Response({'message': 'Repository created successfully', 'repo_id': repo.repo_id}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UserReposView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        user_repos = Repos.objects.filter(user=user)
        serializer = RetrieveReposSerializer(user_repos, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)