from django.urls import path, include 
from rest_framework.routers import DefaultRouter
from .views import  (
    RepositoryViewSet,
    PullRequestViewSet,
    CodeReviewViewSet,
    github_webhook_view
)

router = DefaultRouter()
router.register(r'repositories', RepositoryViewSet, basename='repository')
router.register(r'pull-requests', PullRequestViewSet, basename='pull-request')
router.register(r'reviews', CodeReviewViewSet, basename='review')


urlpatterns = [
    path('webhook/github/', github_webhook_view, name='github-webhook'),
    path('', include(router.urls)),
]
