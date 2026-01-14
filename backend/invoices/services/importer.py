import hashlib
import traceback
from decimal import Decimal
from django.db import transaction
from ..models import InvoiceImport
from ..parsers.vivo import VivoParser
from ..parsers.claro import ClaroParser
from reports.models import Report, Category
from datetime import date

class ImportManager:
    def __init__(self):
        # Mapeamento de operadoras para parsers
        self.parsers = {
            'VIVO': VivoParser(),
            'CLARO': ClaroParser(),
        }

    def get_file_hash(self, file_content):
        sha256_hash = hashlib.sha256()
        
        if hasattr(file_content, 'chunks'):
            # Django UploadedFile
            for chunk in file_content.chunks():
                sha256_hash.update(chunk)
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
        elif hasattr(file_content, 'read'):
            # Generic file-like object (e.g. BytesIO)
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
            for byte_block in iter(lambda: file_content.read(4096), b""):
                sha256_hash.update(byte_block)
            if hasattr(file_content, 'seek'):
                file_content.seek(0)
        else:
            # Path local (string)
            with open(file_content, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def identify_carrier(self, text):
        """Tenta identificar a operadora pelo conteúdo do texto se não informada via path."""
        text_upper = text.upper()
        if 'VIVO' in text_upper or 'TELEFONICA' in text_upper:
            return 'VIVO'
        if 'CLARO' in text_upper or 'EMBRATEL' in text_upper:
            return 'CLARO'
        return None

    def process_invoice(self, file_source, metadata=None, user=None, invoice_instance=None):
        """
        file_source: pode ser InMemoryUploadedFile ou caminho string.
        metadata: dicionário com hints (year, city, carrier, month).
        user: usuário que realizou a ação (para auditoria).
        invoice_instance: Instância já existente do InvoiceImport (opcional).
        """
        file_hash = None
        try:
            # Se já temos a instância e o hash, usamos. Caso contrário calculamos.
            if invoice_instance and invoice_instance.file_hash:
                file_hash = invoice_instance.file_hash
            else:
                file_hash = self.get_file_hash(file_source)
        except Exception as e:
            msg = f"Erro no hash: {str(e)}"
            if invoice_instance:
                invoice_instance.status = InvoiceImport.Status.FAILED
                invoice_instance.error_message = msg
                invoice_instance.error_code = 'HASH_ERROR'
                invoice_instance.save()
            return "FAILED", msg

        # 1. Duplicity check & Re-process logic (Professional Implementation)
        # Se recebemos a instância, ela é a "existing_import".
        existing_import = invoice_instance
        
        # Se não recebemos, tentamos buscar pelo hash
        if not existing_import:
            existing_import = InvoiceImport.objects.filter(file_hash=file_hash).first()
        
        should_reprocess = False
        if existing_import:
            # Bloquear upload somente se existir um Report vinculado e ATIVO (PENDING ou APPROVED)
            if existing_import.report and existing_import.report.status in [Report.Status.PENDING, Report.Status.APPROVED]:
                # Bloqueio Ativo
                if existing_import == invoice_instance:
                     existing_import.status = InvoiceImport.Status.SKIPPED
                     existing_import.error_code = 'DUPLICATE_ACTIVE'
                     existing_import.save()
                return "SKIPPED", "Já Importado (Ativo)"
            
            # Se chegamos aqui, ou o report é None (excluído), ou está CANCELED/FAILED/REVIEW
            should_reprocess = True

        # 2. Extract Data
        safe_metadata = metadata or {}
        carrier_key = safe_metadata.get('carrier', '').upper()
        
        # Usamos o VivoParser como base para extração de texto/ocr inicial se necessário
        base_parser = self.parsers.get('VIVO')
        
        text_sample = ""
        try:
            # Tenta extrair texto para identificação
            text_sample = base_parser.extract_text(file_source)
        except Exception as e:
            # Não falha hard aqui, tenta continuar com parser padrão ou metadata
            print(f"Aviso: Falha na extração de texto preliminar: {e}")
        
        if not carrier_key:
            carrier_key = self.identify_carrier(text_sample)
            
        parser = self.parsers.get(carrier_key) or base_parser
        
        try:
            extracted = parser.parse(file_source) or {}
        except Exception as e:
            error_msg = f"Erro na extração: {str(e)}"
            if existing_import:
                existing_import.status = InvoiceImport.Status.FAILED
                existing_import.error_message = error_msg
                existing_import.error_code = 'EXTRACTION_FAILED'
                if existing_import.report:
                    existing_import.report.status = Report.Status.FAILED
                    existing_import.report.save()
                existing_import.save()
            return "FAILED", error_msg

        # 3. Determine Final Status (InvoiceImport + Report)
        final_import_status = InvoiceImport.Status.SUCCESS
        final_report_status = Report.Status.PENDING
        
        # Validação básica de sucesso
        if not extracted.get('total_value') or extracted.get('total_value') == Decimal('0.00') or not extracted.get('due_date'):
            final_import_status = InvoiceImport.Status.PENDING_REVIEW
            final_report_status = Report.Status.REVIEW
            if existing_import:
                 existing_import.error_code = 'MISSING_REQUIRED_DATA' # Warn only, not failed status

        # 4. Persist
        try:
            with transaction.atomic():
                final_carrier = carrier_key or 'OUTROS'

                import_data = {
                    'file_path': str(file_source),
                    'year': safe_metadata.get('year') or date.today().year,
                    'city': safe_metadata.get('city') or 'N/A',
                    'carrier': final_carrier,
                    'month': safe_metadata.get('month') or date.today().strftime('%B'),
                    'invoice_number': extracted.get('invoice_number'),
                    'due_date': extracted.get('due_date'),
                    'total_value': extracted.get('total_value') or Decimal('0.00'),
                    'confidence_score': extracted.get('confidence', 0),
                    'status': final_import_status,
                    'error_message': None,
                    'error_code': None if final_import_status == InvoiceImport.Status.SUCCESS else 'MISSING_REQUIRED_DATA',
                    'file_hash': file_hash # Ensure hash is set/updated
                }

                if existing_import:
                    # Update Existing
                    from audit.services import AuditService
                    from audit.models import AuditLog
                    from django.forms.models import model_to_dict
                    
                    before_state = model_to_dict(existing_import)
                    
                    for key, value in import_data.items():
                        setattr(existing_import, key, value)
                    
                    # Salva arquivo físico somente se necessário (se file_source for arquivo real e novo)
                    if hasattr(file_source, 'read'):
                        from django.core.files.base import ContentFile
                        if hasattr(file_source, 'seek'): file_source.seek(0)
                        file_content = file_source.read()
                        existing_import.file.save(f"{file_hash}.pdf", ContentFile(file_content), save=False)
                    
                    existing_import.save()

                    # Handle Report Logic (Shared for Update/Create)
                    self._handle_report(existing_import, final_import_status, final_report_status, final_carrier, import_data)
                    
                    AuditService.log_action(
                        user=user,
                        action=AuditLog.Action.REPROCESS,
                        instance=existing_import,
                        before_state=before_state,
                        after_state=model_to_dict(existing_import)
                    )
                    
                    msg = "Fatura processada com sucesso." if final_import_status == InvoiceImport.Status.SUCCESS else "Fatura requer revisão."
                else:
                    # Create New
                    new_import = InvoiceImport(**import_data)
                    new_import.file_hash = file_hash
                    
                    if hasattr(file_source, 'read'):
                        from django.core.files.base import ContentFile
                        if hasattr(file_source, 'seek'): file_source.seek(0)
                        file_content = file_source.read()
                        new_import.file.save(f"{file_hash}.pdf", ContentFile(file_content), save=False)
                    
                    new_import.save()

                    self._handle_report(new_import, final_import_status, final_report_status, final_carrier, import_data)
                    
                    from audit.services import AuditService
                    from audit.models import AuditLog
                    from django.forms.models import model_to_dict
                    
                    AuditService.log_action(
                        user=user,
                        action=AuditLog.Action.IMPORT,
                        instance=new_import,
                        after_state=model_to_dict(new_import)
                    )

                    msg = "Fatura importada com sucesso." if final_import_status == InvoiceImport.Status.SUCCESS else "Fatura requer revisão."
                
                return final_import_status, msg

        except Exception as e:
            print(traceback.format_exc())
            # Ensure failure is recorded in DB if possible
            if existing_import:
                 existing_import.status = InvoiceImport.Status.FAILED
                 existing_import.error_message = f"Erro Persistência: {e}"
                 existing_import.error_code = 'DB_PERSISTENCE_ERROR'
                 existing_import.save()
            return "FAILED", f"Erro no banco de dados: {str(e)}"

    def _handle_report(self, invoice_import, import_status, report_status, carrier, data):
        """Helper to create or update the Report linked to the invoice"""
        if import_status != InvoiceImport.Status.SUCCESS:
            return

        category, _ = Category.objects.get_or_create(name=carrier.capitalize())
        ref_date = data['due_date'] or date.today()
        report_title = f"FATURA {carrier.upper()} - {data['month']}/{data['year']}"

        if invoice_import.report:
            report = invoice_import.report
            report.title = report_title
            report.total_value = data['total_value']
            report.status = report_status
            report.due_date = data['due_date']
            report.reference_date = ref_date
            report.category = category
            report.save()
        else:
            report = Report.objects.create(
                title=report_title,
                reference_date=ref_date,
                due_date=data['due_date'],
                category=category,
                total_value=data['total_value'],
                status=report_status
            )
            invoice_import.report = report
            invoice_import.save()
