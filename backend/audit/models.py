from django.db import models
from django.utils.translation import gettext_lazy as _
from django.conf import settings

class AuditLog(models.Model):
    class Action(models.TextChoices):
        IMPORT = 'IMPORT', _('Importação')
        REPROCESS = 'REPROCESS', _('Reprocessamento')
        UPDATE = 'UPDATE', _('Atualização')
        DELETE = 'DELETE', _('Exclusão')
        APPROVE = 'APPROVE', _('Aprovação')
        REJECT = 'REJECT', _('Rejeição')
        EXPORT = 'EXPORT', _('Download/Exportação')

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Usuário")
    )
    action = models.CharField(max_length=20, choices=Action.choices, verbose_name=_("Ação"))
    entity = models.CharField(max_length=100, verbose_name=_("Entidade"))
    entity_id = models.CharField(max_length=100, verbose_name=_("ID da Entidade")) # CharField for flexibility (e.g. hash or UUID)
    
    before_state = models.JSONField(null=True, blank=True, verbose_name=_("Estado Anterior"))
    after_state = models.JSONField(null=True, blank=True, verbose_name=_("Estado Atual"))
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Data/Hora"))

    class Meta:
        verbose_name = _("Log de Auditoria")
        verbose_name_plural = _("Logs de Auditoria")
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.created_at.strftime('%Y-%m-%d %H:%M')}] {self.user} - {self.action} on {self.entity} ({self.entity_id})"
