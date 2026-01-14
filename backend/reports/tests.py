from decimal import Decimal
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

User = get_user_model()
from .models import Report, Category
from datetime import date, timedelta

class ReportTests(APITestCase):
    def setUp(self):
        # 1. Setup User and Auth
        self.user = User.objects.create_user(
            username='reportuser',
            email='reports@example.com',
            password='password123',
            role='ANALISTA'
        )
        self.client.force_authenticate(user=self.user)

        # 2. Setup Data
        self.category_sales = Category.objects.create(name='Vendas', description='Relatórios de vendas')
        self.category_ops = Category.objects.create(name='Operacional', description='Relatórios operacionais')
        
        self.report1 = Report.objects.create(
            title='Relatório Janeiro',
            reference_date=date(2024, 1, 1),
            category=self.category_sales,
            total_value=Decimal('1000.00'),
            status='PENDING'
        )

        self.list_url = reverse('report-list') # report-list vira do DefaultRouter

    def test_list_reports_authenticated(self):
        """Deve listar relatórios para usuário logado."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Check pagination structure
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Relatório Janeiro')

    def test_list_reports_unauthorized(self):
        """Deve negar acesso a usuário não logado."""
        self.client.force_authenticate(user=None)
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_report_success(self):
        """Deve criar um relatório com payload válido."""
        data = {
            'title': 'Relatório Fevereiro',
            'reference_date': '2024-02-01',
            'category': self.category_sales.id,
            'total_value': '1500.50',
            'status': 'PENDING'
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Report.objects.count(), 2)
        
        created = Report.objects.get(title='Relatório Fevereiro')
        self.assertEqual(created.total_value, Decimal('1500.50'))

    def test_create_report_invalid_payload(self):
        """Deve falhar ao tentar criar relatório sem campos obrigatórios."""
        data = {
            'title': 'Relatório Incompleto'
            # Missing reference_date, category, total_value
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('total_value', response.data)
        self.assertIn('category', response.data)

    def test_update_report_value_only(self):
        """Deve atualizar valores de um relatório (exceto status)."""
        url = reverse('report-detail', args=[self.report1.id])
        data = {
            'total_value': '1200.00'
        }
        # PATCH for partial update
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.report1.refresh_from_db()
        self.assertEqual(self.report1.total_value, Decimal('1200.00'))

    def test_update_report_status_direct_should_fail(self):
        """Deve falhar ao tentar atualizar status diretamente (exige transition)."""
        url = reverse('report-detail', args=[self.report1.id])
        data = {
            'status': 'APPROVED'
        }
        # PATCH for partial update
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("transition", str(response.data))

    def test_delete_report_as_analyst_fails(self):
        """Analista não deve poder excluir relatório (apenas Admin)."""
        url = reverse('report-detail', args=[self.report1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_delete_report_as_admin_success(self):
        """Admin deve poder excluir relatório."""
        # Create Admin User
        admin_user = User.objects.create_user(username='admin_report', password='password', role='ADMIN')
        self.client.force_authenticate(user=admin_user)
        
        url = reverse('report-detail', args=[self.report1.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Report.objects.count(), 0)

    def test_filter_reports(self):
        """Deve filtrar relatórios por status e categoria."""
        # Create another report to test filtering
        Report.objects.create(
            title='Relatório Ops',
            reference_date=date(2024, 1, 2),
            category=self.category_ops,
            total_value=Decimal('500.00'),
            status='APPROVED'
        )

        # Filter by Category ID
        response = self.client.get(self.list_url, {'category': self.category_ops.id})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Relatório Ops')

        # Filter by Status
        response = self.client.get(self.list_url, {'status': 'PENDING'})
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Relatório Janeiro')


