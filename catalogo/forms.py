from django import forms
from .models import Producto
from empresas.models import Empresa


class ProductoForm(forms.ModelForm):
    class Meta:
        model = Producto
        fields = [
            "nombre",
            "descripcion",
            "imagen",
            "precio",
            "stock",
            "activo",
        ]
        widgets = {
            "nombre": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Nombre del producto",
            }),
            "descripcion": forms.Textarea(attrs={
                "class": "form-control",
                "rows": 3,
                "placeholder": "Descripción opcional",
            }),
            "imagen": forms.ClearableFileInput(attrs={
                "class": "form-control",
            }),
            "precio": forms.NumberInput(attrs={
                "class": "form-control",
                "step": "0.01",
                "min": "0",
            }),
            "stock": forms.NumberInput(attrs={
                "class": "form-control",
                "min": "0",
            }),
            "activo": forms.CheckboxInput(attrs={
                "class": "form-check-input",
            }),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        self.empresa_fija = kwargs.pop("empresa_fija", None)
        super().__init__(*args, **kwargs)

        # Si es superusuario, puede elegir la empresa
        if self.user and self.user.is_superuser and not self.empresa_fija:
            self.fields["empresa"] = forms.ModelChoiceField(
                queryset=Empresa.objects.filter(activo=True),
                widget=forms.Select(attrs={"class": "form-select"}),
                label="Empresa",
                required=True,
            )
            field_order = ["empresa"] + list(self.fields.keys())
            self.order_fields(field_order)

    def clean_precio(self):
        precio = self.cleaned_data.get("precio")
        if precio is not None and precio < 0:
            raise forms.ValidationError("El precio no puede ser negativo.")
        return precio

    def clean_nombre(self):
        nombre = self.cleaned_data.get("nombre", "").strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre