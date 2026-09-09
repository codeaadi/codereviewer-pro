from rest_framework import serializers
from .models import Repository, PullRequest, CodeReview, ReviewComment


class ReviewCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewComment
        fields = ['id', 'file_path', 'line_number', 'severity', 'message', 'suggested_patch', 'github_comment_id']
        
        
   
class CodeReviewSerializer(serializers.ModelSerializer):
    comments = ReviewCommentSerializer(many=True, read_only=True)
    
    class Meta:
        model =CodeReview
        fields = [
            'id', 'pull_request', 'status', 'summary'
            'security_risk_score', 'token_usage', 'execution_time_ms',
            'error_message','created_at', 'comments'
        ]        
        
    
class PullRequestSerializer(serializers.ModelSerializer):
    reviews = CodeReviewSerializer(many=True, read_only=True)
    latest_review = serializers.SerializerMethodField()
    
    class Meta:
        model = PullRequest
        fields = [
            'id', 'repository', 'pr_number', 'title',
            'author_username', 'head_sha', 'base_brance',
            'head_branch', 'status', 'created_at', 'updated_at',
            'reviews', 'latest_review'
        ]        
        
        
    def get_latest_review(self, obj):
        latest = obj.reviews.order_by('-created_at').first()
        if latest: 
            return CodeReviewSerializer(latest).data
        return None
    
    
    
    
class RepositorySerializer(serializers.ModelSerializer):
    pull_request_count = serializers.IntegerField(source='pull_request.count',read_only='True')
    
    class Meta:
        model = Repository
        fields = [
            'id', 'owner', 'name', 'full_name',
            'github_repo_id', 'is_active', 'created_at',
            'pull_request_count'
        ]   
        read_only_fields = ['owner', 'created_at']