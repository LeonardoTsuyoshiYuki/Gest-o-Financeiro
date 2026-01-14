from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock
from .services.importer import ImportManager
from .models import InvoiceImport
from reports.models import Report, Category
from decimal import Decimal
from datetime import date

class InvoiceUploadTests(TestCase):
    def setUp(self):
        self.importer = ImportManager()

    @patch('invoices.parsers.vivo.VivoParser.extract_text')
    @patch('invoices.parsers.vivo.VivoParser.parse')
    def test_manual_upload_success(self, mock_parse, mock_extract):
        mock_extract.return_value = "CONTEUDO VIVO"
        mock_parse.return_value = {
            'total_value': Decimal('250.00'),
            'due_date': date(2026, 1, 1),
            'invoice_number': '999',
            'carrier': 'VIVO'
        }
        
        pdf_content = b"%PDF-1.4 test content"
        uploaded_file = SimpleUploadedFile("fatura.pdf", pdf_content, content_type="application/pdf")
        
        status, msg = self.importer.process_invoice(uploaded_file, metadata={})
        
        self.assertEqual(status, InvoiceImport.Status.SUCCESS, msg)
        self.assertEqual(Report.objects.count(), 1)
        self.assertEqual(InvoiceImport.objects.count(), 1)
        
        record = InvoiceImport.objects.first()
        self.assertEqual(record.carrier, "VIVO")
        self.assertEqual(record.due_date, date(2026, 1, 1))

    def test_upload_duplicate_by_hash(self):
        content = b"duplicate content"
        file_hash = self.importer.get_file_hash(SimpleUploadedFile("temp.pdf", content))
        
        active_report = Report.objects.create(
            title="Relatório Ativo",
            reference_date=date(2025, 1, 1),
            category=Category.objects.get_or_create(name="VIVO")[0],
            total_value=Decimal('100.00'),
            status=Report.Status.PENDING
        )

        InvoiceImport.objects.create(
            file_path="old.pdf",
            file_hash=file_hash,
            year=2025, city="X", carrier="VIVO", month="Jan",
            status=InvoiceImport.Status.SUCCESS,
            report=active_report
        )
        
        uploaded_file = SimpleUploadedFile("new.pdf", content, content_type="application/pdf")
        status, msg = self.importer.process_invoice(uploaded_file, metadata={})
        
        self.assertEqual(status, "SKIPPED", f"Status: {status}, Msg: {msg}")
