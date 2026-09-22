import hmac
import hashlib
import json
import os

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response

from .models import Repository, PullRequest, CodeReview
from .serializers import RepositorySerializer, PullRequestSerializer, CodeReviewSerializer
from .task import process_pr_review


def verify_github_signature(payload_body: bytes, secret_token: str, signature_header: str) -> bool:
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
    secret = os.getenv('GITHUB_WEBHOOK_SECRET', '')
    signature = request.headers.get('X-Hub-Signature-256')

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

    action_type = payload.get('action')
    if action_type not in ['opened', 'synchronize', 'reopened']:
        return Response({'msg': f'Action {action_type} skipped.'}, status=status.HTTP_200_OK)

    repo_data = payload.get('repository', {})
    pr_data = payload.get('pull_request', {})

    github_repo_id = repo_data.get('id')
    repository = Repository.objects.filter(github_repo_id=github_repo_id, is_active=True).first()

    if not repository:
        return Response({'error': 'Repository is not registered or is inactive.'}, status=status.HTTP_404_NOT_FOUND)

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

    review = CodeReview.objects.create(
        pull_request=pr_record,
        status='pending'
    )

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

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def test_audit(self, request):
        from django.contrib.auth.models import User

        user, _ = User.objects.get_or_create(
            username='dev_test',
            defaults={'email': 'dev@test.com'}
        )
        repo, _ = Repository.objects.get_or_create(
            owner=user,
            name='security-test-repo',
            defaults={
                'full_name': 'aditya/security-test-repo',
                'github_repo_id': 999888
            }
        )
        pr, _ = PullRequest.objects.get_or_create(
            repository=repo,
            pr_number=1,
            defaults={
                'title': 'Fix search query parameter',
                'author_username': 'test_author',
                'head_sha': '83a1b2c4f2a1b0123456789abcdef0123456789a',
                'base_branch': 'main',
                'head_branch': 'feature/search-fix',
            }
        )

        review = CodeReview.objects.create(pull_request=pr, status='pending')

        process_pr_review(review.id)

        review.refresh_from_db()
        return Response(CodeReviewSerializer(review).data, status=status.HTTP_201_CREATED)
