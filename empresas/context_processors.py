from .models import Empleado


def empresa_actual(request):
    """
    Agrega 'empresa_actual' al contexto de todos los templates.
    - Superusuario → None
    - Empleado activo → su Empresa
    - Otros → None
    """
    if not request.user.is_authenticated:
        return {"empresa_actual": None}

    if request.user.is_superuser:
        return {"empresa_actual": None}

    try:
        empleado = Empleado.objects.select_related("empresa").get(
            usuario=request.user,
            activo=True,
        )
        return {"empresa_actual": empleado.empresa}
    except Empleado.DoesNotExist:
        return {"empresa_actual": None}