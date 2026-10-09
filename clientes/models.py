from django.conf import settings
from django.db import models

from empresas.models import Empresa # Modelo del Tenant (Empresa)


class Cliente(models.Model):
    """Un cliente final, dado de alta por una Empresa y con su propio login."""

    # Primary Key que nos garantiza que cada cliente pertenezca a una sola empresa
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="clientes",
    )
    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cliente",
    )

    nombre = models.CharField(max_length=150)
    direccion_entrega = models.CharField(max_length=255, blank=True)
    telefono = models.CharField(max_length=20)
    saldo_a_favor = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Se actualiza siempre junto con un MovimientoSaldo, nunca a mano.",
    )

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["nombre"]
        constraints = [
            models.UniqueConstraint(
                fields=["empresa", "telefono"],
                name="telefono_unico_por_empresa",
            )
        ]

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"