from django.core.validators import MinValueValidator
from django.db import models

from catalogo.models import Producto
from clientes.models import Cliente


class Pedido(models.Model):
    class Estado(models.TextChoices):
        PENDIENTE = "PEN", "Pendiente"
        ENTREGADO = "ENT", "Entregado"
        CANCELADO = "CAN", "Cancelado"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="pedidos",
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(
        max_length=3,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    total_a_pagar = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-fecha_creacion"]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente.nombre}"

    def recalcular_total(self):
        """Vuelve a sumar los subtotales de DetallePedido. Llamar tras cada cambio de línea."""
        total = self.detalles.aggregate(suma=models.Sum("subtotal"))["suma"] or 0
        self.total_a_pagar = total
        self.save(update_fields=["total_a_pagar"])


class DetallePedido(models.Model):

    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        related_name="detalles",
    )
    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_pedido",
    )
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, editable=False)

    class Meta:
        verbose_name = "Detalle de pedido"
        verbose_name_plural = "Detalles de pedido"

    def __str__(self):
        return f"{self.cantidad} x {self.producto.nombre}"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)


class Pago(models.Model):
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.PROTECT,
        related_name="pagos",
    )
    fecha_pago = models.DateTimeField(auto_now_add=True)
    saldo_utilizado = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    monto_capturado = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        ordering = ["-fecha_pago"]

    def __str__(self):
        return f"Pago de pedido #{self.pedido_id}"


class MovimientoSaldo(models.Model):
    class Tipo(models.TextChoices):
        ABONO = "ABO", "Abono"
        CARGO = "CAR", "Cargo"

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="movimientos_saldo",
    )
    pedido = models.ForeignKey(
        Pedido,
        on_delete=models.SET_NULL,
        related_name="movimientos_saldo",
        null=True,
        blank=True,
    )
    pago = models.ForeignKey(
        Pago,
        on_delete=models.SET_NULL,
        related_name="movimientos_saldo",
        null=True,
        blank=True,
    )
    fecha = models.DateTimeField(auto_now_add=True)
    tipo = models.CharField(max_length=3, choices=Tipo.choices)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    motivo = models.CharField(max_length=255, blank=True)

    class Meta:
        verbose_name = "Movimiento de saldo"
        verbose_name_plural = "Movimientos de saldo"
        ordering = ["-fecha"]

    def __str__(self):
        return f"{self.get_tipo_display()} de {self.monto} - {self.cliente.nombre}"