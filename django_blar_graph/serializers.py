import hashlib

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from django_blar_graph.models import Repos


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'username', 'email', 'groups']


class GroupSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']
        

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
            required=True,
            validators=[UniqueValidator(queryset=User.objects.all())]
            )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['email'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        
        user.set_password(validated_data['password'])
        user.save()

        return user
    
class ReposSerializer(serializers.Serializer):
    github_url = serializers.CharField(max_length=255)
    main_branch = serializers.CharField(max_length=255, required=False, default='main')

    def validate_github_url(self, value):
        if 'github.com' not in value:
            raise serializers.ValidationError("URL must be from GitHub")
        return value
    
    def create(self, validated_data):
        github_url = validated_data['github_url']
        main_branch = validated_data.get('main_branch', 'main')

        # Extract repo name from URL
        repo_name = github_url.split('github.com/')[-1]

        # Calculate hash for id
        id_hash = hashlib.sha256(repo_name.encode()).hexdigest()[:255]

        # Assuming User is available in the request or you have it stored somewhere
        user = self.context['request'].user

        # Create and return the Repos object
        return Repos.objects.create(
            repo_id=id_hash,
            name=repo_name,
            main_branch=main_branch,
            user=user,
            url=github_url
        )

class RetrieveReposSerializer(serializers.ModelSerializer):
    class Meta:
        model = Repos
        exclude = ['user']
          
class CloneRepoSerializer(serializers.Serializer):
    repo_id = serializers.CharField(max_length=255)
    branch = serializers.CharField(max_length=255, required=False)

    def validate_repo_id(self, value):
        # Perform any additional validation here if needed
        return value
    
