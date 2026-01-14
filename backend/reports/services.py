from .models import Report
from audit.services import AuditService
from audit.models import AuditLog
from django.forms.models import model_to_dict
from django.core.exceptions import ValidationError

class ReportWorkflowService:
    # Máquina de estados: { Estado Atual: [Estados Permitidos] }
    ALLOWED_TRANSITIONS = {
        Report.Status.PENDING: [Report.Status.REVIEW, Report.Status.CANCELED],
        Report.Status.REVIEW: [Report.Status.APPROVED, Report.Status.CANCELED, Report.Status.PENDING], # PENDING caso precise voltar
        Report.Status.APPROVED: [], # Estado Final (por enquanto)
        Report.Status.CANCELED: [], # Estado Final
        Report.Status.FAILED: [Report.Status.PENDING, Report.Status.REVIEW], # Pode tentar recuperar
    }

    @classmethod
    def transition_status(cls, report: Report, new_status: str, user, comment: str = None):
        """
        Executa transição de status validando regras e gerando auditoria.
        """
        current_status = report.status
        
        # 1. Validação de Regras de Negócio
        if new_status not in cls.ALLOWED_TRANSITIONS.get(current_status, []):
            # Exceção para superusers ou casos especiais? Por enquanto, regra rígida.
            # Permitir que ADMIN force qualquer status? O prompt diz "Validar transições permitidas"
            # Vamos manter restrito.
            raise ValidationError(f"Transição inválida de '{current_status}' para '{new_status}'.")

        # 2. Regra Específica: Comentário obrigatório para REJEIÇÃO (CANCELED)
        if new_status == Report.Status.CANCELED and not comment:
            raise ValidationError("Comentário é obrigatório ao rejeitar/cancelar um relatório.")

        # 3. Preparar Auditoria
        before_state = model_to_dict(report)
        
        # Determine Action type for Audit
        audit_action = AuditLog.Action.UPDATE
        if new_status == Report.Status.APPROVED:
            audit_action = AuditLog.Action.APPROVE
        elif new_status == Report.Status.CANCELED:
            audit_action = AuditLog.Action.REJECT
        elif new_status == Report.Status.REVIEW:
            audit_action = AuditLog.Action.UPDATE # Review is intermediate

        # 4. Efetivar Mudança
        report.status = new_status
        report.save()

        # 5. Registrar Auditoria com Comentário (se houver)
        after_state = model_to_dict(report)
        if comment:
            after_state['_workflow_comment'] = comment

        AuditService.log_action(
            user=user,
            action=audit_action,
            instance=report,
            before_state=before_state,
            after_state=after_state,
            entity_name="Report"
        )
        
        return report
