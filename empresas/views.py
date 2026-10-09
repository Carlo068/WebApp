from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect

from .models import Empresa, Empleado
from .forms import EmpresaForm

@login_required
def dashboard(request):
    from catalogo.models import Producto
    from clientes.models import Cliente

    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        total_empresas = Empresa.objects.count()
        total_productos = Producto.objects.count()
        total_clientes = Cliente.objects.count()
    else:
        total_empresas = 1 if empresa else 0
        total_productos = Producto.objects.filter(empresa=empresa).count() if empresa else 0
        total_clientes = Cliente.objects.filter(empresa=empresa).count() if empresa else 0

    return render(
        request,
        "dashboard/index.html",
        {
            "total_empresas": total_empresas,
            "total_productos": total_productos,
            "total_clientes": total_clientes,
        },
    )


@login_required
def empresa_lista(request):

    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        empresas = Empresa.objects.all()
    else:
        empresas = Empresa.objects.filter(id=empresa.pk)

    return render(
        request,
        "empresas/lista.html",
        {"empresas": empresas}
    )

def obtener_empresa(usuario):
    """
    Devuelve la empresa del empleado autenticado.
    Si es superusuario, devuelve None.
    """
    if usuario.is_superuser:
        return None

    empleado = Empleado.objects.get(
        usuario=usuario,
        activo=True
    )

    return empleado.empresa

@login_required
def empresa_nueva(request):
    if request.method == "POST":
        form = EmpresaForm(request.POST)
        if form.is_valid():
            form.save()
            
            messages.success(
                request,
                "Empresa registrada correctamente."
            )
            return redirect("empresa_lista")
    else:
        form = EmpresaForm()

    return render(request, "empresas/form.html", {"form": form})


@login_required
def empresa_editar(request, id):
    
    # Validar la vista
    if request.user.is_superuser:
        empresa = get_object_or_404(Empresa, pk=id)
    else:
        empresa_usuario = obtener_empresa(request.user)
        empresa = get_object_or_404(
        Empresa,
        pk=id,
        id=empresa_usuario.pk
    )

    if request.method == "POST":

        form = EmpresaForm(
            request.POST,
            instance=empresa
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Empresa actualizada."
            )

            return redirect("empresa_lista")

    else:

        form = EmpresaForm(
            instance=empresa
        )

    return render(
        request,
        "empresas/form.html",
        {
            "form": form,
            "editar": True,
        }
    )
    
@login_required
def empresa_eliminar(request, id):

    empresa = get_object_or_404(
        Empresa,
        pk=id
    )

    if request.method == "POST":

        empresa.delete()

        messages.success(
            request,
            "Empresa eliminada."
        )

        return redirect("empresa_lista")

    return render(
        request,
        "empresas/eliminar.html",
        {"empresa": empresa}
    )