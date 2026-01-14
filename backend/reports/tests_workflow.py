from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()

from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from reports.models import Report, Category
from audit.models import AuditLog
from datetime import date

class ReportWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='manager', password='password', role='ADMIN')
        self.client.force_authenticate(user=self.user)
        self.category = Category.objects.create(name="Workflow Test")
        self.report = Report.objects.create(
            title="Test Workflow",
            reference_date=date(2025, 1, 1),
            total_value=100.00,
            category=self.category,
            status=Report.Status.PENDING
        )

    def test_transition_success(self):
        url = f'/api/reports/{self.report.pk}/transition/'
        data = {'status': Report.Status.REVIEW}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.report.refresh_from_db()
        self.assertEqual(self.report.status, Report.Status.REVIEW)
        
        # Check Audit
        log = AuditLog.objects.last()
        self.assertEqual(log.action, AuditLog.Action.UPDATE)
        self.assertEqual(log.entity, "Report")

    def test_transition_invalid_flow(self):
        # PENDING -> APPROVED should be blocked (must go via REVIEW)
        url = f'/api/reports/{self.report.pk}/transition/'
        data = {'status': Report.Status.APPROVED}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("inválida", response.data['error'].lower())

    def test_rejection_requires_comment(self):
        url = f'/api/reports/{self.report.pk}/transition/'
        data = {'status': Report.Status.CANCELED} # Canceled = Rejected
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("obrigatório", response.data['error'].lower())

    def test_rejection_with_comment_success(self):
        url = f'/api/reports/{self.report.pk}/transition/'
        data = {'status': Report.Status.CANCELED, 'comment': 'Bad data'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        log = AuditLog.objects.last()
        self.assertEqual(log.action, AuditLog.Action.REJECT)
        self.assertEqual(log.after_state['_workflow_comment'], 'Bad data')
