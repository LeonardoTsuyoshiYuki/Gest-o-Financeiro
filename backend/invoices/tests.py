from django.test import TestCase
from unittest.mock import patch, MagicMock
from .services.scanner import DirectoryScanner
from .services.importer import ImportManager
from .models import InvoiceImport
from reports.models import Report, Category
from datetime import date
from decimal import Decimal

class InvoiceImportTests(TestCase):
    def setUp(self):
        self.base_path = "/tmp/mock_invoices"
        self.scanner = DirectoryScanner(self.base_path)
        self.importer = ImportManager()

    @patch('os.walk')
    def test_scanner_identifies_correct_structure(self, mock_walk):
        mock_walk.return_value = [
            (f"{self.base_path}/2025/Dourados/Vivo/Dezembro", [], ["fatura1.pdf", "foto.jpg"]),
        ]
        
        results = self.scanner.scan()
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['carrier'], 'Vivo')
        self.assertEqual(results[0]['filename'], 'fatura1.pdf')

    @patch('invoices.parsers.vivo.VivoParser.extract_text')
    @patch('invoices.parsers.vivo.VivoParser.parse')
    @patch('builtins.open', new_callable=MagicMock)
    def test_importer_creates_report_and_record(self, mock_file_open, mock_parse, mock_extract):
        mock_file_open.return_value.__enter__.return_value.read.side_effect = [b"content", b""]
        
        mock_extract.return_value = "Fatura número: 12345 Vencimento 10/12/2025 Total a pagar 150,50"
        mock_parse.return_value = {
            'invoice_number': '12345',
            'due_date': date(2025, 12, 10),
            'total_value': Decimal('150.50'),
            'carrier': 'VIVO'
        }

        metadata = {
            'path': f"{self.base_path}/2025/Dourados/Vivo/Dezembro/fatura.pdf",
            'year': '2025',
            'city': 'Dourados',
            'carrier': 'Vivo',
            'month': 'Dezembro'
        }

        status, msg = self.importer.process_invoice(metadata['path'], metadata=metadata)
        
        self.assertEqual(status, "SUCCESS", msg)
        self.assertEqual(InvoiceImport.objects.count(), 1)
        
        report = Report.objects.first()
        self.assertIsNotNone(report)
        self.assertEqual(report.total_value, Decimal('150.50'))

    @patch('builtins.open', new_callable=MagicMock)
    def test_duplicate_avoidance(self, mock_file_open):
        import hashlib
        expected_hash = hashlib.sha256(b"same_content").hexdigest()
        mock_file_open.return_value.__enter__.return_value.read.side_effect = [b"same_content", b""]
        
        inv = InvoiceImport.objects.create(
            file_path="old/path.pdf",
            file_hash=expected_hash,
            year=2025, city="X", carrier="Y", month="Z"
        )
        cat = Category.objects.create(name="CatTest")
        report = Report.objects.create(
            title="Old Report", total_value=Decimal('10'), status=Report.Status.PENDING,
            reference_date=date.today(), due_date=date.today(), category=cat
        )
        inv.report = report
        inv.save()
        
        metadata = {
            'path': "new/path.pdf",
            'carrier': 'Vivo', 'year': '2025', 'city': 'X', 'month': 'Z'
        }
        
        status, msg = self.importer.process_invoice(metadata['path'], metadata=metadata)
        self.assertEqual(status, "SKIPPED", msg)
