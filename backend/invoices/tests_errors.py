from django.test import TestCase
from unittest.mock import patch, MagicMock
from decimal import Decimal
from .models import InvoiceImport
from .services.importer import ImportManager
from reports.models import Report

class InvoiceErrorTests(TestCase):
    def setUp(self):
        self.importer = ImportManager()
    
    @patch('invoices.services.importer.ImportManager.get_file_hash')
    def test_hash_error(self, mock_hash):
        mock_hash.side_effect = Exception("Hash failure")
        status, msg = self.importer.process_invoice("path/to.pdf", metadata={'carrier': 'VIVO'})
        self.assertEqual(status, 'FAILED')
        self.assertIn("Erro no hash", msg)
        # Note: No instance created so no error_code in DB unless we passed instance.
        
    @patch('invoices.services.importer.ImportManager.get_file_hash')
    @patch('invoices.parsers.vivo.VivoParser.parse')
    def test_extraction_error_sets_code(self, mock_parse, mock_hash):
        mock_hash.return_value = "hash123"
        # Simulate View creating the object first (PROCESSING)
        InvoiceImport.objects.create(file_hash="hash123", status='PROCESSING', year=2026, city='A', carrier='VIVO', month='Jan')
        
        mock_parse.side_effect = Exception("OCR crashed")
        
        status, msg = self.importer.process_invoice("path/to.pdf", metadata={'carrier': 'VIVO'})
        
        self.assertEqual(status, 'FAILED')
        inv = InvoiceImport.objects.first()
        self.assertIsNotNone(inv) # Should exist
        self.assertEqual(inv.status, 'FAILED')
        # Note: logic only updates DB if existing_import is found.
        # Since we created it with hash123, logic finds it via filter(file_hash).
        self.assertEqual(inv.error_code, 'EXTRACTION_FAILED')
        self.assertIn("OCR crashed", inv.error_message)

    @patch('invoices.services.importer.ImportManager.get_file_hash')
    @patch('invoices.parsers.vivo.VivoParser.parse')
    def test_missing_data_sets_code_review(self, mock_parse, mock_hash):
        mock_hash.return_value = "hash456"
        # Returns empty dict -> missing total_val
        mock_parse.return_value = {} 
        
        status, msg = self.importer.process_invoice("path/to.pdf", metadata={'carrier': 'VIVO'})
        
        self.assertEqual(status, 'PENDING_REVIEW')
        inv = InvoiceImport.objects.first()
        self.assertEqual(inv.status, 'PENDING_REVIEW')
        self.assertEqual(inv.error_code, 'MISSING_REQUIRED_DATA')

    @patch('invoices.services.importer.ImportManager.get_file_hash')
    @patch('invoices.parsers.vivo.VivoParser.parse')
    def test_duplicate_active_skipped(self, mock_parse, mock_hash):
        mock_hash.return_value = "hash789"
        mock_parse.return_value = {'total_value': Decimal('100'), 'due_date': '2026-01-01'}
        
        # 1. First import setup manually
        inv = InvoiceImport.objects.create(file_hash="hash789", status='SUCCESS', year=2026, city='A', carrier='VIVO', month='Jan')
        from reports.models import Report, Category
        cat = Category.objects.create(name="C2") # Unique name
        rep = Report.objects.create(title="T", status=Report.Status.PENDING, reference_date='2026-01-01', total_value=10, category=cat)
        inv.report = rep
        inv.save()
        
        # 2. Second import (same hash)
        status, msg = self.importer.process_invoice("path/to.pdf", metadata={'carrier': 'VIVO'})
        
        self.assertEqual(status, 'SKIPPED')
        
        inv.refresh_from_db()
        # Verify it wasn't changed
        self.assertEqual(inv.status, 'SUCCESS') 

    @patch('invoices.services.importer.ImportManager.get_file_hash')
    def test_duplicate_active_with_instance_updates_code(self, mock_hash):
        mock_hash.return_value = "hash999"
        
        # Create existing
        inv = InvoiceImport.objects.create(file_hash="hash999", status='SUCCESS', year=2026, city='A', carrier='VIVO', month='Jan')
        from reports.models import Report, Category
        cat = Category.objects.create(name="C")
        rep = Report.objects.create(title="T", status=Report.Status.PENDING, reference_date='2026-01-01', total_value=10, category=cat)
        inv.report = rep
        inv.save()
        
        # Call process with SAME instance (simulating Task picking it up but finding it's a dupe logic? 
        # No, duplicate logic usually implies we found ANOTHER record with same hash.
        # If we pass `invoice_instance`, it IS `existing_import`.
        # Logic says: if existing_import... check report.
        # If active report -> block.
        # If existing_import == invoice_instance -> SKIPPED.
        
        status, msg = self.importer.process_invoice("path/to.pdf", invoice_instance=inv)
        self.assertEqual(status, 'SKIPPED')
        
        inv.refresh_from_db()
        self.assertEqual(inv.status, 'SKIPPED')
        self.assertEqual(inv.error_code, 'DUPLICATE_ACTIVE')
