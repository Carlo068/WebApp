from django.conf import settings
from django.db import models


class Empresa(models.Model):
    """Cada fila es una empresa cliente de la plataforma (un 'tenant')."""

    nombre = models.CharField(max_length=150)
    contacto = models.CharField(max_length=150, blank=True)
    fecha_registro = models.DateField(auto_now_add=True)
    activo = models.BooleanField(
        default=True,
        help_text="Permite desactivar una empresa sin borrar su historial.",
    )

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Empleado(models.Model):
    """
    Une un usuario de Django (login) con la Empresa a la que pertenece.
    Una empresa puede tener varios Empleados; cada Empleado tiene su propia cuenta.
    """

    usuario = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="empleado",
    )
    empresa = models.ForeignKey(
        Empresa,
        on_delete=models.PROTECT,
        related_name="empleados",
    )
    activo = models.BooleanField(default=True)
    fecha_ingreso = models.DateField(auto_now_add=True)

    class Meta:
        verbose_name = "Empleado"
        verbose_name_plural = "Empleados"
        ordering = ["empresa", "usuario__username"]

    def __str__(self):
        nombre = self.usuario.get_full_name() or self.usuario.username
        return f"{nombre} ({self.empresa.nombre})"