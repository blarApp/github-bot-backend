from django.contrib.auth.models import User
from django.db import models


class Integration(models.Model):
    SOURCE_CHOICES = (
        ("github", "github"),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES, default="github")
    api_key = models.CharField(max_length=255, null=True, blank=True)
    def __str__(self):
        return f"{self.user.username} @ {self.source}"
    

    
class Repos(models.Model):
    repo_id = models.CharField(max_length=255, null=False, blank=True, primary_key=True)
    name = models.CharField(max_length=255, null=False)
    main_branch = models.CharField(max_length=255, null=True, blank=True, default='main')
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=False, blank=False)
    last_updated = models.DateTimeField(auto_now=True)
    url = models.CharField(max_length=255)
    def __str__(self):
            return f"{self.user.username} @ {self.name}"  # Changed from self.repo_name to self.name
    
