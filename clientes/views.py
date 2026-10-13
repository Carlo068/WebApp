from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator

from empresas.views import obtener_empresa

from .models import Cliente
from .forms import ClienteForm

@login_required 
def cliente_lista(request):

    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        clientes = Cliente.objects.select_related("empresa").all()
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")

        clientes = Cliente.objects.filter(empresa=empresa).select_related("empresa")

    q = request.GET.get("q", "").strip()
    if q:
        clientes = clientes.filter(nombre__icontains=q)

    clientes = clientes.order_by("nombre")

    paginator = Paginator(clientes, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(
        request, 
        "clientes/lista.html", 
        {
            "page_obj": page_obj,
            "q": q
        }
    )


@login_required
@permission_required('clientes.add_cliente', raise_exception=True)
def cliente_nuevo(request):
    empresa = obtener_empresa(request.user)

    if not request.user.is_superuser and not empresa:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ClienteForm(request.POST)
        if form.is_valid():

            cliente = form.save(commit=False)

            if request.user.is_superuser and "empresa" in form.cleaned_data:
                cliente.empresa = form.cleaned_data["empresa"]
            else:
                cliente.empresa = empresa

            cliente.usuario = request.user

            cliente.save()
            messages.success(
                request, f"Cliente «{cliente.nombre}» creado correctamente."
            )

            return redirect("cliente_lista")
    else:
        form = ClienteForm()

    return render(
        request,
        "clientes/form.html",
        {
            "form": form,
            "editar": False,
        },
    )


@login_required
def cliente_editar(request, id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        cliente = get_object_or_404(Cliente, pk=id)
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        cliente = get_object_or_404(Cliente, pk=id, empresa=empresa)

    if request.method == "POST":

        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            cliente = form.save(commit=False)

            if not request.user.is_superuser:
                cliente.empresa = empresa

            cliente.save()
            messages.success(
                request, f"Cliente «{cliente.nombre}» actualizado."
            )
            return redirect("cliente_lista")
    else:
        form = ClienteForm(instance=cliente)

    return render(
        request,
        "clientes/form.html",
        {
            "form": form,
            "editar": True,
            "cliente": cliente,
        },
    )


@login_required
def cliente_eliminar(request, id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        cliente = get_object_or_404(Cliente, pk=id)
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")

        cliente = get_object_or_404(Cliente, pk=id, empresa=empresa)

    if request.method == "POST":
        nombre = cliente.nombre
        cliente.delete()
        messages.success(request, f"Cliente «{nombre}» eliminado.")
        return redirect("cliente_lista")

    return render(
        request,
        "clientes/eliminar.html",
        {
            "cliente": cliente,
        },
    )