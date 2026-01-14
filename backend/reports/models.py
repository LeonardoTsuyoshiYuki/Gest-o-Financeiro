from django.db import models
from django.utils.translation import gettext_lazy as _

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name=_("Nome"))
    description = models.TextField(blank=True, verbose_name=_("Descrição"))
    
    class Meta:
        verbose_name = _("Categoria")
        verbose_name_plural = _("Categorias")

    def __str__(self):
        return self.name

class Report(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pendente')
        APPROVED = 'APPROVED', _('Aprovado')
        CANCELED = 'CANCELED', _('Cancelado')
        FAILED = 'FAILED', _('Falha')
        REVIEW = 'REVIEW', _('Aguardando Revisão')

    title = models.CharField(max_length=200, verbose_name=_("Título"))
    reference_date = models.DateField(verbose_name=_("Data de Referência"))
    category = models.ForeignKey(
        Category, 
        on_delete=models.PROTECT, 
        related_name='reports',
        verbose_name=_("Categoria")
    )
    total_value = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        verbose_name=_("Valor Total")
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name=_("Status")
    )
    
    due_date = models.DateField(null=True, blank=True, verbose_name=_("Data de Vencimento"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Criado em"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Atualizado em"))

    class Meta:
        verbose_name = _("Relatório")
        verbose_name_plural = _("Relatórios")
        ordering = ['-reference_date']

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
