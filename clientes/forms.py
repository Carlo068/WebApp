from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente

        fields = ["nombre", "direccion_entrega", "telefono"]
        widgets = {
            "nombre": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Nombre del cliente",
                }
            ),
            "direccion_entrega": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Dirección",
                }
            ),
            "telefono": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Teléfono",
                }
            )
        }