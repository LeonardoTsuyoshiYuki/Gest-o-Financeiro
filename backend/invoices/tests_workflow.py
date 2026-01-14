from django.test import TestCase
from django.contrib.auth import get_user_model
User = get_user_model()
from decimal import Decimal
from datetime import date
from .models import InvoiceImport
from .services.reviewer import InvoiceReviewer
from audit.models import AuditLog

class InboxWorkflowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='reviewer', password='password')
        
        # Create an INBOX invoice
        self.invoice = InvoiceImport.objects.create(
            file_hash="abc123hash",
            year=2025,
            city="Goiania",
            carrier="VIVO",
            month="Janeiro",
            status=InvoiceImport.Status.INBOX,
            total_value=Decimal('150.00'),
            confidence_score=80
        )

    def test_confirmation_creates_report(self):
        # Confirm without changes
        updated_invoice = InvoiceReviewer.confirm_invoice(
            self.invoice.id, self.user, {}
        )
        
        self.assertEqual(updated_invoice.status, InvoiceImport.Status.SUCCESS)
        self.assertIsNotNone(updated_invoice.report)
        self.assertEqual(updated_invoice.report.total_value, Decimal('150.00'))
        self.assertEqual(updated_invoice.confidence_score, 80) # No change penalty

        # Audit check
        logs = AuditLog.objects.filter(entity="Report")
        self.assertTrue(logs.exists())
        self.assertEqual(logs.first().action, AuditLog.Action.IMPORT)

    def test_confirmation_with_changes_penalizes_score(self):
        # Reviewer fixes the value
        data = {'total_value': '200.00'}
        
        updated_invoice = InvoiceReviewer.confirm_invoice(
            self.invoice.id, self.user, data
        )
        
        self.assertEqual(updated_invoice.total_value, Decimal('200.00'))
        self.assertEqual(updated_invoice.report.total_value, Decimal('200.00'))
        # Should be penalized to 30
        self.assertEqual(updated_invoice.confidence_score, 30)

        # Audit check
        log = AuditLog.objects.filter(entity="InvoiceImport (Review)").first()
        self.assertEqual(log.action, AuditLog.Action.UPDATE)
