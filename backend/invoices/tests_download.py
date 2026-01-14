from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import InvoiceImport
from reports.models import Report
from django.contrib.auth import get_user_model
User = get_user_model()
from decimal import Decimal
from datetime import date

import traceback

class InvoiceDownloadTests(TestCase):
    def setUp(self):
        try:
            self.client = APIClient()
            self.user = User.objects.create_user(username='testuser', password='password')
            self.client.force_authenticate(user=self.user)

            # Create sample InvoiceImport with file
            file_content = b"PDF CONTENT MOCK"
            self.pdf_file = SimpleUploadedFile("fatura_test.pdf", file_content, content_type="application/pdf")
            
            self.invoice = InvoiceImport(
                file_hash="hash_test_123",
                year=2025,
                month="Janeiro",
                city="Teste City",
                carrier="VIVO",
                total_value=Decimal('100.00'),
                due_date=date(2025, 1, 10),
                invoice_number="12345"
            )
            self.invoice.file.save("fatura_test.pdf", self.pdf_file, save=True)
        except Exception:
            traceback.print_exc()
            raise

    def test_download_success(self):
        url = reverse('invoice-download', args=[self.invoice.id])
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'application/pdf')
        self.assertIn('attachment; filename="fatura_hash_tes.pdf"', response['Content-Disposition'])
        self.assertEqual(b"".join(response.streaming_content), b"PDF CONTENT MOCK")

    def test_download_unauthenticated(self):
        self.client.logout()
        url = reverse('invoice-download', args=[self.invoice.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_download_not_found(self):
        url = reverse('invoice-download', args=[99999])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_download_missing_file(self):
        # Create invoice without file
        inv_no_file = InvoiceImport.objects.create(
            file_hash="hash_no_file",
            year=2025,
            month="Fev",
            city="X",
            carrier="CLARO"
        )
        url = reverse('invoice-download', args=[inv_no_file.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data['error'], "Arquivo físico não encontrado para esta fatura.")
