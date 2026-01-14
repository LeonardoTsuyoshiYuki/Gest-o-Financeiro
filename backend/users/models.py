from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """
    Custom User model where email is the unique identifier.
    """
    email = models.EmailField(unique=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrador')
        GESTOR = 'GESTOR', _('Gestor')
        ANALISTA = 'ANALISTA', _('Analista')
        VISUALIZADOR = 'VISUALIZADOR', _('Visualizador')

    role = models.CharField(
        max_length=20, 
        choices=Role.choices, 
        default=Role.VISUALIZADOR,
        verbose_name=_("Função")
    )

    def __str__(self):
        return f"{self.email} ({self.get_role_display()})"
