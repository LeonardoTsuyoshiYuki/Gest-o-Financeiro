from rest_framework import views, response, status, permissions, parsers
from .services.scanner import DirectoryScanner
from .services.importer import ImportManager
import os
from django.db import IntegrityError, transaction

from .tasks import process_invoice_task
from .models import InvoiceImport
from datetime import date

from users.permissions import IsAdmin, IsGestor, IsAnalyst, IsViewer

class TriggerInvoiceImportView(views.APIView):
    """Varredura automática de pasta local (Async)."""
    permission_classes = [IsAnalyst]

    def post(self, request):
        base_path = request.data.get('base_path', r'G:\Controle de TI\Planilhas de controles\Despesas T.I')
        
        if not os.path.exists(base_path):
             return response.Response(
                {"error": f"Caminho não encontrado ou inacessível: {base_path}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        scanner = DirectoryScanner(base_path)
        importer = ImportManager() # Helper for hash
        
        found_files = scanner.scan()
        dispatched_count = 0
        
        for file_meta in found_files:
            try:
                # Calculate hash from file path
                with open(file_meta['path'], 'rb') as f:
                     file_hash = importer.get_file_hash(f)
                
                # Atomic Get or Create
                invoice, created = InvoiceImport.objects.get_or_create(
                    file_hash=file_hash,
                    defaults={
                        'file_path': file_meta['path'],
                        'year': file_meta.get('year') or date.today().year,
                        'city': file_meta.get('city') or 'N/A',
                        'carrier': file_meta.get('carrier') or 'OUTROS',
                        'month': file_meta.get('month') or 'N/A',
                        'status': InvoiceImport.Status.PROCESSING
                    }
                )

                if not created:
                    invoice.status = InvoiceImport.Status.PROCESSING
                    invoice.save()
                
                # Dispatch Task
                process_invoice_task.delay(invoice.id, request.user.id)
                dispatched_count += 1
            except Exception as e:
                print(f"Error preparing task for {file_meta['path']}: {e}")
                continue
            
        return response.Response({
            "message": "Processamento em segundo plano iniciado",
            "files_found": len(found_files),
            "tasks_dispatched": dispatched_count
        })

class InvoiceUploadView(views.APIView):
    """Upload manual via Frontend (Async)."""
    permission_classes = [IsAnalyst]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def post(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return response.Response({"error": "Nenhum arquivo enviado."}, status=status.HTTP_400_BAD_REQUEST)

        if not file_obj.name.lower().endswith('.pdf'):
            return response.Response({"error": "Apenas arquivos PDF são permitidos."}, status=status.HTTP_400_BAD_REQUEST)

        importer = ImportManager()
        try:
            # Hash
            if hasattr(file_obj, 'seek'): file_obj.seek(0)
            file_hash = importer.get_file_hash(file_obj)
            
            # Atomic Get OR Init (Can't use get_or_create easily with file save logic effectively, 
            # but we can try lock or handling integrity error)
            
            invoice = InvoiceImport.objects.filter(file_hash=file_hash).first()
            created = False
            
            if not invoice:
                try:
                    invoice = InvoiceImport.objects.create(
                        file_path=file_obj.name,
                        file_hash=file_hash,
                        year=date.today().year,
                        city='Upload Manual',
                        carrier='Desconhecido',
                        month='N/A',
                        status=InvoiceImport.Status.PROCESSING
                    )
                    created = True
                except IntegrityError:
                    # Race condition caught
                    invoice = InvoiceImport.objects.get(file_hash=file_hash)
                    created = False

            if not created:
                invoice.status = InvoiceImport.Status.PROCESSING
                invoice.save()

            # Always save/refresh the file content if it's an upload
            # But wait, if we overwrite, we might break history if hashes collide but content differs?
            # Hash implies content is same. So overwriting is redundant but safe.
            
            from django.core.files.base import ContentFile
            if hasattr(file_obj, 'seek'): file_obj.seek(0)
            content = file_obj.read()
            invoice.file.save(f"{file_hash}.pdf", ContentFile(content), save=True)
            
            # Dispatch
            process_invoice_task.delay(invoice.id, request.user.id)
            
            return response.Response({
                "status": "PROCESSING",
                "message": "Upload recebido. Processamento iniciado (Async)." if created else "Fatura já existente. Reprocessamento iniciado.",
                "id": invoice.id
            }, status=status.HTTP_202_ACCEPTED)

        except Exception as e:
            return response.Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InvoiceDownloadView(views.APIView):
    """
    Download do PDF original da fatura.
    """
    permission_classes = [IsViewer]

    def get(self, request, pk):
        from .models import InvoiceImport
        from django.http import FileResponse, Http404
        from datetime import date

        try:
            invoice = InvoiceImport.objects.get(pk=pk)
        except InvoiceImport.DoesNotExist:
            return response.Response({"error": "Fatura não encontrada."}, status=status.HTTP_404_NOT_FOUND)

        if not invoice.file:
             return response.Response(
                {"error": "Arquivo físico não encontrado para esta fatura."}, 
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # Audit log using AuditService
            from audit.services import AuditService
            from audit.models import AuditLog
            
            AuditService.log_action(
                user=request.user,
                action=AuditLog.Action.EXPORT,
                instance=invoice,
                entity_name="InvoiceImport"
            )
            
            # Open file handle
            handle = invoice.file.open('rb')
            response_file = FileResponse(handle, content_type='application/pdf')
            response_file['Content-Disposition'] = f'attachment; filename="fatura_{invoice.file_hash[:8]}.pdf"'
            return response_file
        except Exception as e:
            return response.Response({"error": f"Erro ao ler arquivo: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class InvoiceInboxView(views.APIView):
    """
    Lista faturas aguardando revisão (Status = INBOX, PROCESSING, OCR_RUNNING).
    """
    permission_classes = [IsViewer]

    def get(self, request):
        from .models import InvoiceImport
        from django.forms.models import model_to_dict
        from django.utils import timezone
        from datetime import timedelta
        
        # --- Rescue Stale Jobs Strategy ---
        # If a task has been PROCESSING or OCR_RUNNING for more than 5 minutes, 
        # assume the worker died or hung. Mark as FAILED.
        timeout_threshold = timezone.now() - timedelta(minutes=5)
        stale_jobs = InvoiceImport.objects.filter(
            status__in=[InvoiceImport.Status.PROCESSING, InvoiceImport.Status.OCR_RUNNING],
            updated_at__lt=timeout_threshold
        )
        if stale_jobs.exists():
            stale_count = stale_jobs.update(
                status=InvoiceImport.Status.FAILED,
                error_message="Timeout: O processamento demorou muito e foi abortado. Tente novamente.",
                error_code="TIMEOUT_ERROR"
            )
            print(f"Rescued {stale_count} stale invoice tasks.")
        # ----------------------------------

        statuses = [
            InvoiceImport.Status.INBOX, 
            InvoiceImport.Status.PROCESSING, 
            InvoiceImport.Status.OCR_RUNNING,
            InvoiceImport.Status.PENDING_REVIEW,
            InvoiceImport.Status.SKIPPED,
            InvoiceImport.Status.FAILED # Also show failed so user knows
        ]
        inbox_items = InvoiceImport.objects.filter(status__in=statuses).order_by('-created_at')
        
        # Simple serialization
        data = []
        for item in inbox_items:
            data.append({
                'id': item.id,
                'file_path': item.file.url if item.file else None,
                'carrier': item.carrier,
                'invoice_number': item.invoice_number,
                'due_date': item.due_date,
                'total_value': float(item.total_value) if item.total_value else 0.0,
                'confidence_score': item.confidence_score,
                'created_at': item.created_at,
                'status': item.status,
                'error_message': item.error_message, # Exposed error message to frontend
                'error_code': item.error_code
            })
            
        return response.Response(data)

class InvoiceConfirmView(views.APIView):
    """
    Confirma e gera relatório.
    """
    permission_classes = [IsAnalyst]

    def post(self, request, pk):
        from .services.reviewer import InvoiceReviewer
        
        try:
            # Data from body: total_value, due_date, carrier, invoice_number
            InvoiceReviewer.confirm_invoice(pk, request.user, request.data)
            return response.Response({"message": "Fatura confirmada e relatório gerado."})
        except Exception as e:
            import traceback
            traceback.print_exc()
            return response.Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
