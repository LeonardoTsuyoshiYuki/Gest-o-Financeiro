from django.db import models
from django.utils.translation import gettext_lazy as _
from reports.models import Report

class InvoiceImport(models.Model):
    class Status(models.TextChoices):
        INBOX = 'INBOX', _('Caixa de Entrada')
        PROCESSING = 'PROCESSING', _('Processando')
        OCR_RUNNING = 'OCR_RUNNING', _('OCR em Execução')
        PENDING = 'PENDING', _('Pendente')
        SUCCESS = 'SUCCESS', _('Sucesso')
        FAILED = 'FAILED', _('Falha')
        SKIPPED = 'SKIPPED', _('Pulados (Duplicado)')
        PENDING_REVIEW = 'PENDING_REVIEW', _('Aguardando Revisão')

    file_path = models.CharField(max_length=500, verbose_name=_("Caminho do Arquivo"))
    file = models.FileField(upload_to='invoices/%Y/%m/', null=True, blank=True, verbose_name=_("Arquivo PDF"))
    file_hash = models.CharField(max_length=64, unique=True, verbose_name=_("Hash do Arquivo"))
    
    # Metadata extracted from path
    year = models.IntegerField(verbose_name=_("Ano"))
    city = models.CharField(max_length=100, verbose_name=_("Cidade"))
    carrier = models.CharField(max_length=100, verbose_name=_("Operadora"))
    month = models.CharField(max_length=20, verbose_name=_("Mês"))
    
    # Data extracted from PDF
    invoice_number = models.CharField(max_length=100, blank=True, null=True, verbose_name=_("Número da Fatura"))
    due_date = models.DateField(blank=True, null=True, verbose_name=_("Data de Vencimento"))
    total_value = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name=_("Valor Total"))
    
    # Relationship with existing Report
    report = models.OneToOneField(
        Report, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='invoice_source'
    )
    
    status = models.CharField(
        max_length=20, 
        choices=Status.choices, 
        default=Status.PENDING
    )
    error_message = models.TextField(blank=True, null=True)
    error_code = models.CharField(max_length=50, blank=True, null=True, verbose_name=_("Código do Erro"))
    confidence_score = models.IntegerField(
        default=0, 
        verbose_name=_("Confiabilidade"),
        help_text="0-100 score of parsing confidence"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Importação de Fatura")
        verbose_name_plural = _("Importações de Faturas")
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.carrier} - {self.city} - {self.month}/{self.year}"
