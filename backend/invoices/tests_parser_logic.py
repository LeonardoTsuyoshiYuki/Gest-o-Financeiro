from django.test import TestCase
from decimal import Decimal
from datetime import date
from io import BytesIO
from unittest.mock import patch, MagicMock
from .parsers.vivo import VivoParser
from .services.importer import ImportManager
from .models import InvoiceImport
from reports.models import Report

class VivoParserLogicTests(TestCase):
    def setUp(self):
        self.parser = VivoParser()

    def test_vivo_parser_complex_text(self):
        text = """
        VIVO EMPRESAS
        Informações de Pagamento:
        Data de vencimento 17/01/2026
        Total a pagar R$ 3.340,61
        Nº da fatura 000012345
        """
        with patch.object(VivoParser, 'extract_text', return_value=text):
            data = self.parser.parse("fake_path.pdf")
            self.assertEqual(data['total_value'], Decimal('3340.61'))
            self.assertEqual(data['due_date'], date(2026, 1, 17))

class ImportReprocessTests(TestCase):
    def setUp(self):
        self.importer = ImportManager()

    @patch('invoices.parsers.vivo.VivoParser.parse')
    @patch('invoices.parsers.vivo.VivoParser.extract_text')
    def test_reprocess_deleted_report(self, mock_extract, mock_parse):
        mock_extract.return_value = "VIVO"
        mock_parse.return_value = {
            'invoice_number': '123', 'due_date': date(2025, 12, 10), 'total_value': Decimal('100.00'), 'confidence': 100
        }
        file_content = b"pdf content reprocess delete"
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf = SimpleUploadedFile("fatura.pdf", file_content)
        
        # 1. Importa com sucesso
        status1, _ = self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2025, 'month': 'Dez', 'city': 'Y'})
        self.assertEqual(status1, 'SUCCESS')
        
        # 2. Exclui o relatório manualmente (ex via Admin ou Frontend)
        imp = InvoiceImport.objects.first()
        imp.report.delete()
        
        # 3. Tenta importar de novo (deve permitir porque o report foi excluído)
        pdf.seek(0)
        status2, msg2 = self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2025, 'month': 'Dez', 'city': 'Y'})
        self.assertEqual(status2, 'SUCCESS')
        self.assertIn("Fatura processada com sucesso", msg2)
        self.assertEqual(InvoiceImport.objects.count(), 1) # Auditável: Mantém o mesmo registro
        
        imp.refresh_from_db()
        self.assertIsNotNone(imp.report) # Deve ter criado um novo report

    @patch('invoices.parsers.vivo.VivoParser.parse')
    @patch('invoices.parsers.vivo.VivoParser.extract_text')
    def test_reprocess_canceled_report(self, mock_extract, mock_parse):
        mock_extract.return_value = "VIVO"
        mock_parse.return_value = {
            'invoice_number': '123', 'due_date': date(2025, 12, 10), 'total_value': Decimal('100.00'), 'confidence': 100
        }
        file_content = b"pdf content reprocess cancel"
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf = SimpleUploadedFile("fatura.pdf", file_content)
        
        # 1. Importa com sucesso
        self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2025, 'month': 'Dez', 'city': 'Y'})
        
        # 2. Cancela o relatório
        imp = InvoiceImport.objects.first()
        report = imp.report
        report.status = Report.Status.CANCELED
        report.save()
        
        # 3. tenta importar de novo
        pdf.seek(0)
        status2, msg2 = self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2025, 'month': 'Dez', 'city': 'Y'})
        self.assertEqual(status2, 'SUCCESS')
        self.assertIn("Fatura processada com sucesso", msg2)

    @patch('invoices.parsers.vivo.VivoParser.parse')
    @patch('invoices.parsers.vivo.VivoParser.extract_text')
    def test_block_active_report(self, mock_extract, mock_parse):
        mock_extract.return_value = "VIVO"
        mock_parse.return_value = {
            'invoice_number': '123', 'due_date': date(2025, 12, 10), 'total_value': Decimal('100.00'), 'confidence': 100
        }
        file_content = b"pdf content active block"
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf = SimpleUploadedFile("fatura.pdf", file_content)
        
        # 1. Importa com sucesso (Status PENDING por padrão)
        self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2025, 'month': 'Dez', 'city': 'Y'})
        
        # 2. Tenta importar de novo (deve bloquear com mensagem específica)
        pdf.seek(0)
        status2, msg2 = self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2025, 'month': 'Dez', 'city': 'Y'})
        self.assertEqual(status2, 'SKIPPED')
        self.assertEqual(msg2, "Já Importado (Ativo)")

    @patch('invoices.parsers.vivo.VivoParser.parse')
    @patch('invoices.parsers.vivo.VivoParser.extract_text')
    def test_reprocess_updates_data(self, mock_extract, mock_parse):
        # 1. Primeira extração falha (campos vazios)
        mock_extract.return_value = "Fatura sem dados"
        mock_parse.return_value = {} # Empty parse result
        
        file_content = b"pdf content update audit"
        from django.core.files.uploadedfile import SimpleUploadedFile
        pdf = SimpleUploadedFile("fatura.pdf", file_content)
        
        status1, _ = self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2026, 'city': 'X', 'month': 'Jan'})
        self.assertEqual(status1, 'PENDING_REVIEW')
        
        imp = InvoiceImport.objects.first()
        self.assertEqual(imp.total_value, Decimal('0.00'))
        
        # 2. Segunda extração corrigida
        mock_extract.return_value = "Total a pagar R$ 500,00 Vencimento 10/10/2026"
        mock_parse.return_value = {
            'invoice_number': '123', 'due_date': date(2026, 10, 10), 'total_value': Decimal('500.00'), 'confidence': 90
        }
        pdf.seek(0)
        status2, _ = self.importer.process_invoice(pdf, metadata={'carrier': 'VIVO', 'year': 2026, 'city': 'X', 'month': 'Jan'})
        
        self.assertEqual(status2, 'SUCCESS')
        imp.refresh_from_db()
        self.assertEqual(imp.total_value, Decimal('500.00'))
        self.assertEqual(imp.report.total_value, Decimal('500.00'))
        self.assertEqual(imp.report.status, Report.Status.PENDING)
