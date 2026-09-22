import logging
from celery import shared_task
from django.db import transaction
from .models import CodeReview, ReviewComment
from .services.ai_auditor import AIAuditorService

logger = logging.getLogger(__name__)

@shared_task(bind=True, max_retries=3)
def process_pr_review(self, review_id: int, mock_diff: str = None):
    """
    Asynchronous task:
    1. Loads CodeReview record.
    2. Runs Groq AI Auditor on the diff.
    3. Persists summary, risk score, and line-by-line review comments in an atomic transaction.
    """
    try:
        review = CodeReview.objects.get(id=review_id)
        review.status = 'processing'
        review.save(update_fields=['status'])

        # If a mock/test diff wasn't provided, use a default sample diff
        diff_content = mock_diff or """diff --git a/users/views.py b/users/views.py
index 83a1b2c..4f2a1b0 100644
--- a/users/views.py
+++ b/users/views.py
@@ -12,4 +12,8 @@ def search_user(request):
     query = request.GET.get('q', '')
+    # Raw query without parameterized inputs
+    cursor = connection.cursor()
+    cursor.execute(f"SELECT * FROM auth_user WHERE username = '{query}'")
+    return JsonResponse({'results': cursor.fetchall()})
"""

        auditor = AIAuditorService()
        result = auditor.audit_diff(diff_content)

        data = result['data']

        with transaction.atomic():
            review.status = 'completed'
            review.summary = data.get('summary', 'Audit complete.')
            review.security_risk_score = data.get('security_risk_score', 0)
            review.token_usage = result['token_usage']
            review.execution_time_ms = result['execution_time_ms']
            review.save()

            for finding in data.get('findings', []):
                ReviewComment.objects.create(
                    review=review,
                    file_path=finding.get('file_path', 'unknown'),
                    line_number=finding.get('line_number', 1),
                    severity=finding.get('severity', 'info'),
                    message=finding.get('message', ''),
                    suggested_patch=finding.get('suggested_patch', '')
                )

        logger.info(f"CodeReview #{review_id} successfully completed.")
        return f"Review #{review_id} processed."

    except Exception as exc:
        logger.error(f"Error processing review #{review_id}: {str(exc)}")
        try:
            review = CodeReview.objects.get(id=review_id)
            review.status = 'failed'
            review.error_message = str(exc)
            review.save(update_fields=['status', 'error_message'])
        except Exception:
            pass
        raise self.retry(exc=exc, countdown=10)
    