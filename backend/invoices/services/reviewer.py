from django.shortcuts import get_object_or_404
from django.db import transaction
from django.forms.models import model_to_dict
from datetime import date
from decimal import Decimal
from ..models import InvoiceImport
from reports.models import Report, Category
from audit.services import AuditService
from audit.models import AuditLog

class InvoiceReviewer:
    @staticmethod
    def confirm_invoice(invoice_id, user, data):
        """
        Confirma uma fatura da INBOX:
        1. Atualiza dados da InvoiceImport com o payload (correção manual).
        2. Recalcula score de confiabilidade (penalidade se alterado).
        3. Cria o Report oficial.
        4. Move InvoiceImport para status SUCCESS (ou PENDING_REVIEW se ainda estranho?).
           Assumimos que 'Confirmar' = Validado pelo humano.
        """
        
        with transaction.atomic():
            invoice = get_object_or_404(InvoiceImport, pk=invoice_id)
            before_state = model_to_dict(invoice)
            
            # 1. Update Invoice Data
            fields_to_update = ['total_value', 'due_date', 'invoice_number', 'carrier']
            changed = False
            
            # Normalizar dados de entrada e comparar
            for field in fields_to_update:
                new_val = data.get(field)
                if new_val is not None:
                    # Type conversion for comparison logic if needed
                    # (Simplified for brevity, DRF serializer usually handles types before passed here)
                    # For now assuming data comes cleaned or we simply assign.
                    
                    old_val = getattr(invoice, field)
                    # Simple comparison (str conversion for safe compare)
                    if str(new_val) != str(old_val if old_val is not None else ''):
                        setattr(invoice, field, new_val)
                        changed = True

            # 2. Penalty logic
            if changed:
                # Se humano alterou, o score original não vale mais.
                # Mas se humano validou, teoricamente é 100% confiável agora?
                # O requisito diz: "Alterações manuais reduzem confidence_score."
                # Talvez "reduce confidence of AUTOMATION".
                # Se o humano tocou, o dado está correto, mas o 'extraction quality' foi ruim.
                # Vamos setar para 100 (confiança no dado final) ou 30 (qualidade da extração)?
                # Requisito: "Ajuste manual: <=30". Entendido. Isso indica que a extração foi ruim.
                invoice.confidence_score = 30
            else:
                # Se apenas confirmou sem mudar nada, e o score era baixo,
                # o score deveria subir para 100 (validado)? 
                # Requisito: "OCR validado: 80".
                # Se o user confirma "Está certo", vira 100?
                # Vamos manter a lógica: Se editou, 30. Se só confirmou, mantém ou sobe?
                # O prompt diz "Ajuste manual: <=30".
                # Vou aplicar 30 se houve edição. Se não houve, mantenho o original ou 100?
                # Vou manter o original se não houve edição, pois reflete a qualidade da automação.
                pass

            invoice.status = InvoiceImport.Status.SUCCESS
            invoice.save()

            AuditService.log_action(
                user=user,
                action=AuditLog.Action.UPDATE,
                instance=invoice,
                before_state=before_state,
                after_state=model_to_dict(invoice),
                entity_name="InvoiceImport (Review)"
            )

            # 3. Create Report
            final_carrier = invoice.carrier or 'OUTROS'
            category, _ = Category.objects.get_or_create(name=final_carrier.capitalize())
            
            # Título padrão
            month_map = {
                1: 'Janeiro', 2: 'Fevereiro', 3: 'Março', 4: 'Abril', 5: 'Maio', 6: 'Junho',
                7: 'Julho', 8: 'Agosto', 9: 'Setembro', 10: 'Outubro', 11: 'Novembro', 12: 'Dezembro'
            }
            ref_date = invoice.due_date or date.today()
            month_name = month_map.get(ref_date.month, str(ref_date.month))
            report_title = f"FATURA {final_carrier} - {month_name}/{ref_date.year}"

            report = Report.objects.create(
                title=report_title,
                reference_date=ref_date,
                due_date=invoice.due_date,
                category=category,
                total_value=invoice.total_value or Decimal('0.00'),
                status=Report.Status.PENDING # Starts as Pending approval workflow
            )
            
            # Link back
            invoice.report = report
            invoice.save()
            
            AuditService.log_action(
                user=user,
                action=AuditLog.Action.IMPORT, # Report created via confirmation logic
                instance=report,
                after_state=model_to_dict(report),
                entity_name="Report"
            )

            invoice.refresh_from_db()
            return invoice
