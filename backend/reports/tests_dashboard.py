from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
User = get_user_model()

from .models import Report, Category
from decimal import Decimal
from datetime import date, timedelta

class DashboardEndpointsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='password', role='ANALISTA')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name="Telecom")
        
        # Create Reports
        # 1. Approved
        Report.objects.create(title="R1", reference_date=date(2025,1,1), total_value=100.00, category=self.category, status=Report.Status.APPROVED)
        # 2. Pending
        Report.objects.create(title="R2", reference_date=date(2025,1,1), total_value=50.00, category=self.category, status=Report.Status.PENDING)
        # 3. Overdue (Pending with old due_date)
        Report.objects.create(title="R3", reference_date=date(2025,1,1), due_date=date(2024,12,31), total_value=200.00, category=self.category, status=Report.Status.PENDING)
        # 4. Canceled
        Report.objects.create(title="R4", reference_date=date(2025,2,1), total_value=300.00, category=self.category, status=Report.Status.CANCELED)

    def test_status_summary(self):
        url = reverse('dashboard-status-summary')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Check Approved
        self.assertEqual(data['APPROVED']['count'], 1)
        self.assertEqual(data['APPROVED']['total'], 100.00)
        
        # Check Pending (Should handle both pending reports? Yes, aggregation counts all)
        # R2 (50) + R3 (200) = 250
        self.assertEqual(data['PENDING']['count'], 2)
        self.assertEqual(data['PENDING']['total'], 250.00)
        
        # Check Overdue (R3 only)
        # R3 is PENDING and due_date < today (assuming today is > 2024-12-31, which is true in mock environment 2026)
        self.assertEqual(data['OVERDUE']['count'], 1)
        self.assertEqual(data['OVERDUE']['total'], 200.00)

    def test_timeline(self):
        url = reverse('dashboard-timeline')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Expected:
        # 2025-01: APPROVED:100, PENDING:250
        # 2025-02: CANCELED:300
        
        month1 = next(item for item in data if item['month'] == '2025-01-01')
        self.assertEqual(month1['APPROVED'], 100.00)
        self.assertEqual(month1['PENDING'], 250.00)
        
        month2 = next(item for item in data if item['month'] == '2025-02-01')
        self.assertEqual(month2['CANCELED'], 300.00)
