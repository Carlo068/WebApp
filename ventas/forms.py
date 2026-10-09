from django import forms
from clientes.models import Cliente
from .models import Producto

from .models import DetallePedido, Pedido, Pago


class PedidoForm(forms.ModelForm):
    class Meta:
        model = Pedido
        fields = ["cliente"]
        widgets = {
            "cliente": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, user=None, empresa=None, **kwargs):
        super().__init__(*args, **kwargs)
        if empresa:
            self.fields["cliente"].queryset = Cliente.objects.filter(
                empresa=empresa
            )
        elif user and user.is_superuser:
            self.fields["cliente"].queryset = Cliente.objects.all()


class DetallePedidoForm(forms.ModelForm):
    class Meta:
        model = DetallePedido
        fields = ["producto", "cantidad"]
        widgets = {
            "producto": forms.Select(attrs={"class": "form-select"}),
            "cantidad": forms.NumberInput(
                attrs={"class": "form-control", "min": "1", "value": "1"}
            ),
        }

    def __init__(self, *args, empresa=None, user=None, **kwargs):
        super().__init__(*args, **kwargs)

        if empresa:
            self.fields["producto"].queryset = Producto.objects.filter(
                empresa=empresa, activo=True
            )
        elif user and user.is_superuser:
            self.fields["producto"].queryset = Producto.objects.filter(
                activo=True
            )

class PagoForm(forms.ModelForm):
    class Meta:
        model = Pago
        fields = ["saldo_utilizado", "monto_capturado"]
        labels = {
            "saldo_utilizado": "Usar saldo a favor del cliente",
            "monto_capturado": "Monto en efectivo / tarjeta",
        }
        widgets = {
            "saldo_utilizado": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
            "monto_capturado": forms.NumberInput(
                attrs={"class": "form-control", "step": "0.01", "min": "0"}
            ),
        }