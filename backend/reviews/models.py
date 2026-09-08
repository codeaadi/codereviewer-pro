from django.db import models
from django.contrib.auth.models import User

class Repository(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='repositories')
    name = models.CharField(max_length=255)
    full_name = models.CharField(max_length=255, unique=True)
    github_repo_id = models.BigIntegerField(unique=True)
    is_active = models.BooleanField(default=True)
    webhook_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.full_name
    
    
class PullRequest(models.Model):
    STATUS_CHOICES = (
        ('open', 'Open'),
        ('closed', 'Closed'),
        ('merged', 'Merged'),
    )    
    
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE, related_name='pull_request')
    pr_number = models.PositiveIntegerField()
    title = models.CharField(max_length=500)
    author_username = models.CharField(max_length=255)
    head_sha = models.CharField(max_length=40)
    base_branch = models.CharField(max_length=255)
    head_branch = models.CharField(max_length=255)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='open')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class  Meta:
        unique_together = ('repository', 'pr_number')
        
    def __str__(self):
        return f'{self.repository.full_name} #{self.pr_number} - {self.title}'  
    
    
      
class CodeReview(models.Model):
    STATUS_CHOICES = (
        ('pemding', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    )
    
    pull_request = models.ForeignKey(PullRequest, on_delete=models.CASCADE, related_name='reviews')
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    summary = models.TextField(blank=True)
    security_risk_score = models.IntegerField(default=0)
    token_usage = models.IntegerField(default=0)
    execution_time_ms = models.IntegerField(default=0)
    error_message = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'Review for PR #{self.pull_request.pr_number} [{self.status}]'
    
    
  
class ReviewComment(models.Model):
    SEVERITY_CHOICES = (
        ('info', 'Info'),
        ('warning','Warning'),
        ('critical', 'Critical'),
    )    
    
    review = models.ForeignKey(CodeReview, on_delete=models.CASCADE, related_name='comments')
    file_path = models.CharField(max_length=1000)
    line_number = models.PositiveIntegerField()
    severity = models.CharField(max_length=10, choices=SEVERITY_CHOICES, default='info')
    message = models.TextField()
    suggested_patch = models.TextField(blank=True)
    github_comment_id = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return f'{self.severity.upper()} on {self.file_path}:{self.line_number}'
    
    