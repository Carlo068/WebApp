from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import get_object_or_404, render, redirect
from django.core.paginator import Paginator

from .models import Producto
from .forms import ProductoForm
from empresas.views import obtener_empresa


@login_required
def producto_lista(request):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        productos = Producto.objects.select_related("empresa").all()
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        productos = Producto.objects.filter(empresa=empresa).select_related("empresa")

    # Búsqueda simple
    q = request.GET.get("q", "").strip()
    if q:
        productos = productos.filter(nombre__icontains=q)

    # Filtro activo
    estado = request.GET.get("estado", "")
    if estado == "activo":
        productos = productos.filter(activo=True)
    elif estado == "inactivo":
        productos = productos.filter(activo=False)

    productos = productos.order_by("nombre")

    paginator = Paginator(productos, 12)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(request, "catalogo/lista.html", {
        "page_obj": page_obj,
        "q": q,
        "estado": estado,
    })


@login_required
def producto_nuevo(request):
    empresa = obtener_empresa(request.user)

    if not request.user.is_superuser and not empresa:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect("dashboard")

    if request.method == "POST":
        form = ProductoForm(
            request.POST,
            request.FILES,
            user=request.user,
            empresa_fija=empresa,
        )
        if form.is_valid():
            producto = form.save(commit=False)

            if request.user.is_superuser and "empresa" in form.cleaned_data:
                producto.empresa = form.cleaned_data["empresa"]
            else:
                producto.empresa = empresa

            producto.save()
            messages.success(request, f"Producto «{producto.nombre}» creado correctamente.")
            return redirect("producto_lista")
    else:
        form = ProductoForm(user=request.user, empresa_fija=empresa)

    return render(request, "catalogo/form.html", {
        "form": form,
        "editar": False,
    })


@login_required
def producto_editar(request, id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        producto = get_object_or_404(Producto, pk=id)
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        producto = get_object_or_404(Producto, pk=id, empresa=empresa)

    if request.method == "POST":
        form = ProductoForm(
            request.POST,
            request.FILES,
            instance=producto,
            user=request.user,
            empresa_fija=empresa,
        )
        if form.is_valid():
            producto = form.save(commit=False)

            if not request.user.is_superuser:
                producto.empresa = empresa
            elif "empresa" in form.cleaned_data:
                producto.empresa = form.cleaned_data["empresa"]

            producto.save()
            messages.success(request, f"Producto «{producto.nombre}» actualizado.")
            return redirect("producto_lista")
    else:
        form = ProductoForm(
            instance=producto,
            user=request.user,
            empresa_fija=empresa,
        )

    return render(request, "catalogo/form.html", {
        "form": form,
        "editar": True,
        "producto": producto,
    })


@login_required
def producto_eliminar(request, id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        producto = get_object_or_404(Producto, pk=id)
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        producto = get_object_or_404(Producto, pk=id, empresa=empresa)

    if request.method == "POST":
        nombre = producto.nombre
        producto.delete()
        messages.success(request, f"Producto «{nombre}» eliminado.")
        return redirect("producto_lista")

    return render(request, "catalogo/eliminar.html", {
        "producto": producto,
    })