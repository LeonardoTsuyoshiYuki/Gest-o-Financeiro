from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
from reports.models import Report, Category
from invoices.models import InvoiceImport
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

User = get_user_model()

class DashboardInsightsTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='insight_user', password='password', role='ANALISTA')
        self.client.force_authenticate(user=self.user)
        
        self.category = Category.objects.create(name="Telecom")
        
        # Datas
        today = date.today()
        first_this_month = today.replace(day=1)
        last_month = first_this_month - timedelta(days=1)
        first_last_month = last_month.replace(day=1)
        
        # 1. Reports Mês Atual
        Report.objects.create(title="R1", reference_date=first_this_month, total_value=1000.00, category=self.category, status=Report.Status.APPROVED)
        Report.objects.create(title="R2", reference_date=first_this_month, total_value=500.00, category=self.category, status=Report.Status.PENDING)
        
        # 2. Reports Mês Anterior
        Report.objects.create(title="R3_Old", reference_date=first_last_month, total_value=1200.00, category=self.category, status=Report.Status.APPROVED)
        
        # 3. Invoices (Erros e Duplicatas Mês Atual)
        # Note: InvoiceImport usa created_at (DateTimeField), então usamos timezone.now
        InvoiceImport.objects.create(
            file_hash="hash_fail", year=today.year, month="X", city="Y", carrier="Z",
            status=InvoiceImport.Status.FAILED, error_code="HASH_ERROR"
        )
        InvoiceImport.objects.create(
            file_hash="hash_skip", year=today.year, month="X", city="Y", carrier="Z",
            status=InvoiceImport.Status.SKIPPED, error_code="DUPLICATE_ACTIVE"
        )

    def test_insights_endpoint_structure(self):
        url = reverse('dashboard-insights')
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data
        
        # Validar Campos Principais
        self.assertIn('current_month_total', data)
        self.assertIn('last_month_total', data)
        self.assertIn('variation_percent', data)
        self.assertIn('import_errors_count', data)
        self.assertIn('skipped_count', data)
        self.assertIn('insights_list', data)
        
        # Validar Valores
        # Mês atual: 1000 + 500 = 1500
        self.assertEqual(Decimal(str(data['current_month_total'])), Decimal('1500.00'))
        
        # Mês anterior: 1200
        self.assertEqual(Decimal(str(data['last_month_total'])), Decimal('1200.00'))
        
        # Variação: (1500 - 1200) / 1200 = 0.25 (25%)
        self.assertEqual(data['variation_percent'], 25.0)
        
        # Contagens de Invoice
        self.assertEqual(data['import_errors_count'], 1)
        self.assertEqual(data['skipped_count'], 1)
        
        # Ver se gerou texto de insight
        self.assertTrue(len(data['insights_list']) > 0)
        # Check for partial match to avoid formatting slight differences
        self.assertTrue(any("Aumento" in s and "25.0%" in s for s in data['insights_list']))
