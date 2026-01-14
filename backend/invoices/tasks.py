from celery import shared_task
from django.db import transaction
from .models import InvoiceImport
from .services.importer import ImportManager
from audit.services import AuditService
from audit.models import AuditLog
from django.forms.models import model_to_dict
import os

@shared_task(bind=True)
def process_invoice_task(self, invoice_import_id, user_id=None):
    """
    Task to process an uploaded invoice automatically.
    """
    invoice = None
    try:
        invoice = InvoiceImport.objects.get(pk=invoice_import_id)
        
        # Update status to PROCESSING (if not already)
        if invoice.status != InvoiceImport.Status.PROCESSING:
             invoice.status = InvoiceImport.Status.PROCESSING
             invoice.save()
        
        # Initialize Importer
        importer = ImportManager()
        
        if not invoice.file:
             raise ValueError("No file associated with InvoiceImport")

        file_path = invoice.file.path
        
        from django.contrib.auth import get_user_model
        User = get_user_model()
        user = User.objects.get(pk=user_id) if user_id else None

        # Execute processing
        invoice.status = InvoiceImport.Status.OCR_RUNNING
        invoice.save()

        # Pass invoice instance to avoid duplicate lookups/race conditions
        status, msg = importer.process_invoice(file_path, user=user, invoice_instance=invoice)
        
        return f"Processed {invoice.id}: {status}"

    except Exception as e:
        # Fail handler
        # Fail handler
        if invoice:
            invoice.status = InvoiceImport.Status.FAILED
            invoice.error_message = f"Critical Task Failure: {str(e)}"
            invoice.error_code = 'CRITICAL_TASK_FAILURE'
            invoice.save(update_fields=["status", "error_message", "error_code"])
        raise e
