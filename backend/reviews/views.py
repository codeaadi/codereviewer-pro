import hmac
import hashlib
import json
import os

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

from .models import Repository, PullRequest, CodeReview
from .serializers import RepositorySerializer, PullRequestSerializer, CodeReviewSerializer


def verify_github_signature(payload_body: bytes, secret_token: str, signature_header: str) -> bool:
    """Verifies that the webhook request came directly from GitHub using HMAC-SHA256."""
    if not signature_header or not secret_token:
        return False
    hash_type, signature = signature_header.split('=', 1)
    if hash_type != 'sha256':
        return False
    mac = hmac.new(secret_token.encode('utf-8'), msg=payload_body, digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature)


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def github_webhook_view(request):
    """
    Webhook receiver for GitHub events.
    Verifies HMAC signature, registers PRs, and queues code review tasks.
    """
    secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    signature = request.headers.get('X-Hub-Signature-256')

    # Enforce signature verification when secret is configured
    if secret:
        if not verify_github_signature(request.body, secret, signature):
            return Response({'error': 'Invalid signature'}, status=status.HTTP_403_FORBIDDEN)

    event = request.headers.get('X-GitHub-Event', 'ping')
    if event == 'ping':
        return Response({'msg': 'Pong! Webhook verified successfully.'}, status=status.HTTP_200_OK)

    if event != 'pull_request':
        return Response({'msg': f'Event {event} ignored.'}, status=status.HTTP_200_OK)

    try:
        payload = json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        return Response({'error': 'Malformed JSON'}, status=status.HTTP_400_BAD_REQUEST)

    action = payload.get('action')
    if action not in ['opened', 'synchronize', 'reopened']:
        return Response({'msg': f'Action {action} skipped.'}, status=status.HTTP_200_OK)

    repo_data = payload.get('repository', {})
    pr_data = payload.get('pull_request', {})

    github_repo_id = repo_data.get('id')
    repository = Repository.objects.filter(github_repo_id=github_repo_id, is_active=True).first()

    if not repository:
        return Response({'error': 'Repository is not registered or is inactive.'}, status=status.HTTP_404_NOT_FOUND)

    # Ingest or update the Pull Request record
    pr_record, _ = PullRequest.objects.update_or_create(
        repository=repository,
        pr_number=pr_data.get('number'),
        defaults={
            'title': pr_data.get('title', 'Untitled'),
            'author_username': pr_data.get('user', {}).get('login', 'unknown'),
            'head_sha': pr_data.get('head', {}).get('sha', ''),
            'base_branch': pr_data.get('base', {}).get('ref', 'main'),
            'head_branch': pr_data.get('head', {}).get('ref', ''),
            'status': 'open',
        }
    )

    # Initialize a pending CodeReview record
    review = CodeReview.objects.create(
        pull_request=pr_record,
        status='pending'
    )

    # TODO (Phase 4): Dispatch celery worker task to parse git diff and call Groq AI
    # run_pr_code_review.delay(review.id)

    return Response({
        'message': 'Pull request received and review queued.',
        'pr_number': pr_record.pr_number,
        'review_id': review.id
    }, status=status.HTTP_202_ACCEPTED)


class RepositoryViewSet(viewsets.ModelViewSet):
    serializer_class = RepositorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Repository.objects.filter(owner=self.request.user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class PullRequestViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PullRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return PullRequest.objects.filter(
            repository__owner=self.request.user
        ).order_by('-updated_at')


class CodeReviewViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CodeReviewSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CodeReview.objects.filter(
            pull_request__repository__owner=self.request.user
        ).order_by('-created_at')
    
