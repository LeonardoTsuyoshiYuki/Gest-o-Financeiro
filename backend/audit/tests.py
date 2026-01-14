from django.test import TestCase
from django.contrib.auth.models import User
from decimal import Decimal
from datetime import date
from .models import AuditLog
from .services import AuditService
from reports.models import Report, Category

class AuditSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='auditor', password='password')
        self.category = Category.objects.create(name="Audit Test")
        self.report = Report.objects.create(
            title="Test Report",
            reference_date=date(2025, 1, 1),
            total_value=Decimal('100.00'),
            category=self.category
        )

    def test_log_creation(self):
        AuditService.log_action(
            user=self.user,
            action=AuditLog.Action.UPDATE,
            instance=self.report,
            before_state={'status': 'PENDING'},
            after_state={'status': 'APPROVED'}
        )
        
        log = AuditLog.objects.last()
        self.assertIsNotNone(log)
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.action, AuditLog.Action.UPDATE)
        self.assertEqual(log.entity, "Report")
        self.assertEqual(log.entity_id, str(self.report.pk))
        self.assertEqual(log.before_state['status'], 'PENDING')
        self.assertEqual(log.after_state['status'], 'APPROVED')

    def test_log_without_user(self):
        AuditService.log_action(
            user=None,
            action=AuditLog.Action.IMPORT,
            instance=self.report
        )
        log = AuditLog.objects.last()
        self.assertIsNone(log.user)
        self.assertEqual(log.action, AuditLog.Action.IMPORT)

    def test_json_serialization(self):
        # Test serialization of Decimal and Date
        AuditService.log_action(
            user=self.user,
            action=AuditLog.Action.UPDATE,
            instance=self.report,
            after_state={'value': Decimal('100.00'), 'date': date(2025, 1, 1)}
        )
        log = AuditLog.objects.last()
        self.assertEqual(log.after_state['value'], '100.00')
        self.assertEqual(log.after_state['date'], '2025-01-01')
