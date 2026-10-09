from django.core.validators import MinValueValidator
from django.db import models

from empresas.models import Empresa


def ruta_imagen_producto(instance, filename):
    """Organiza las imágenes en carpetas separadas por empresa."""
    return f"productos/empresa_{instance.empresa_id}/{filename}"


class Producto(models.Model):
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="productos",
    )
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)
    imagen = models.ImageField(
        upload_to=ruta_imagen_producto,
        blank=True,
        null=True,
    )
    precio = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(0)],
    )
    stock = models.PositiveIntegerField(
        default=0,
        help_text="Cantidad disponible en inventario (se descuenta al generarse un pedido).",
    )
    activo = models.BooleanField(
        default=True,
        help_text="Si está apagado, el producto no aparece en el catálogo aunque tenga stock.",
    )

    class Meta:
        verbose_name = "Producto"
        verbose_name_plural = "Productos"
        ordering = ["nombre"]

    def __str__(self):
        return f"{self.nombre} ({self.empresa.nombre})"