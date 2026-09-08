from django.contrib import admin
from .models import Repository, PullRequest, CodeReview, ReviewComment

@admin.register(Repository)
class RepositoryAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'owner', 'is_active', 'created_at')
    search_fields = ('name', 'full_name')
    
    
@admin.register(PullRequest)
class PullRequestAdmin(admin.ModelAdmin):
    list_display = ('repository', 'pr_number', 'title', 'author_username', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('title', 'author_username')
    
    
@admin.register(CodeReview)
class CodeReviewAdmin(admin.ModelAdmin):
    list_display = ('pull_request', 'status', 'security_risk_score', 'created_at')
    list_filter = ('status',)
    
    
@admin.register(ReviewComment)
class ReviewCommentsAdmin(admin.ModelAdmin):
    list_display = ('review', 'file_path', 'line_number', 'severity')
    list_filter = ('severity',)    
    
        
