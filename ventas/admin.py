from django.contrib import admin

from ventas.models import DetallePedido, MovimientoSaldo, Pago, Pedido

# Register your models here.
admin.site.register(Pedido)
admin.site.register(DetallePedido)
admin.site.register(Pago)
admin.site.register(MovimientoSaldo)