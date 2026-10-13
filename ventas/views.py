from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render
from django.db import transaction

from empresas.views import obtener_empresa

from .forms import DetallePedidoForm, PedidoForm, PagoForm
from .models import DetallePedido, Pedido, MovimientoSaldo


@login_required
def pedido_lista(request):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        pedidos = Pedido.objects.select_related("cliente__empresa", "cliente").all()
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        pedidos = Pedido.objects.filter(cliente__empresa=empresa).select_related("cliente")

    q = request.GET.get("q", "").strip()
    if q:
        pedidos = pedidos.filter(cliente__nombre__icontains=q)

    pedidos = pedidos.order_by("-id")

    paginator = Paginator(pedidos, 10)
    page = request.GET.get("page")
    page_obj = paginator.get_page(page)

    return render(
        request,
        "ventas/lista.html",
        {
            "page_obj": page_obj,
            "q": q,
        },
    )


@login_required
def pedido_crear(request):
    empresa = obtener_empresa(request.user)

    if not request.user.is_superuser and not empresa:
        messages.error(request, "No tienes una empresa asignada.")
        return redirect("dashboard")

    if request.method == "POST":
        form = PedidoForm(request.POST, user=request.user, empresa=empresa)
        if form.is_valid():
            pedido = form.save(commit=False)

            if hasattr(pedido, "usuario"):
                pedido.usuario = request.user

            pedido.total_a_pagar = 0
            pedido.save()

            messages.success(
                request, f"Pedido #{pedido.id} creado. Agrega los productos."
            )
            return redirect("pedido_detalle", pk=pedido.pk)
    else:
        form = PedidoForm(user=request.user, empresa=empresa)

    return render(
        request,
        "ventas/form.html",
        {
            "form": form,
            "editar": False,
        },
    )


@login_required
def pedido_detalle(request, pk):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        pedido = get_object_or_404(Pedido, pk=pk)
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        pedido = get_object_or_404(Pedido, pk=pk, cliente__empresa=empresa)

    detalles = pedido.detalles.select_related("producto").all()

    pagos = pedido.pagos.all()
    total_pagado = sum(p.saldo_utilizado + p.monto_capturado for p in pagos)
    saldo_pendiente = max(pedido.total_a_pagar - total_pagado, 0)
    esta_pagado = pedido.total_a_pagar > 0 and total_pagado >= pedido.total_a_pagar

    form_detalle = DetallePedidoForm(
        empresa=pedido.cliente.empresa, user=request.user
    )
    form_pago = PagoForm(
        initial={"saldo_utilizado": 0, "monto_capturado": saldo_pendiente}
    )

    return render(
        request,
        "ventas/detalle.html",
        {
            "pedido": pedido,
            "detalles": detalles,
            "pagos": pagos,
            "total_pagado": total_pagado,
            "saldo_pendiente": saldo_pendiente,
            "esta_pagado": esta_pagado,
            "form_detalle": form_detalle,
            "form_pago": form_pago
        },
    )


@login_required
def registrar_pago(request, pedido_id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        pedido = get_object_or_404(Pedido, pk=pedido_id)
    else:
        pedido = get_object_or_404(Pedido, pk=pedido_id, cliente__empresa=empresa)

    cliente = pedido.cliente

    if request.method == "POST":
        form = PagoForm(request.POST)
        if form.is_valid():
            saldo_utilizado = form.cleaned_data.get("saldo_utilizado") or 0
            monto_capturado = form.cleaned_data.get("monto_capturado") or 0
            monto_total_pago = saldo_utilizado + monto_capturado

            if monto_total_pago <= 0:
                messages.error(request, "El monto del pago debe ser mayor a $0.00.")
                return redirect("pedido_detalle", pk=pedido.id)

            saldo_a_favor = getattr(cliente, "saldo_a_favor", 0)
            if saldo_utilizado > saldo_a_favor:
                messages.error(
                    request,
                    f"El cliente solo tiene ${saldo_a_favor} de saldo a favor.",
                )
                return redirect("pedido_detalle", pk=pedido.id)

            total_pagado_actual = sum(
                p.saldo_utilizado + p.monto_capturado for p in pedido.pagos.all()
            )
            deuda_pendiente = max(pedido.total_a_pagar - total_pagado_actual, 0)

            with transaction.atomic():
                pago = form.save(commit=False)
                pago.pedido = pedido
                pago.save()

                if saldo_utilizado > 0:
                    cliente.saldo_a_favor -= saldo_utilizado
                    MovimientoSaldo.objects.create(
                        cliente=cliente,
                        pedido=pedido,
                        pago=pago,
                        tipo="CAR",
                        monto=saldo_utilizado,
                        motivo=f"Uso de saldo en Pedido #{pedido.id}",
                    )

                if monto_total_pago > deuda_pendiente:
                    sobrante = monto_total_pago - deuda_pendiente
                    cliente.saldo_a_favor += sobrante
                    MovimientoSaldo.objects.create(
                        cliente=cliente,
                        pedido=pedido,
                        pago=pago,
                        tipo="ABO",
                        monto=sobrante,
                        motivo=f"Excedente de pago en Pedido #{pedido.id}",
                    )

                cliente.save()

            messages.success(request, f"Pago de ${monto_total_pago} registrado.")

    return redirect("pedido_detalle", pk=pedido.id)

@login_required
def agregar_detalle(request, pedido_id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        pedido = get_object_or_404(Pedido, pk=pedido_id)
    else:
        pedido = get_object_or_404(Pedido, pk=pedido_id, cliente__empresa=empresa)

    if request.method == "POST":
        form_detalle = DetallePedidoForm(
            request.POST, empresa=pedido.cliente.empresa, user=request.user
        )
        if form_detalle.is_valid():
            detalle = form_detalle.save(commit=False)
            detalle.pedido = pedido
            detalle.precio_unitario = detalle.producto.precio
            detalle.save()
            
            subtotal = detalle.cantidad * detalle.precio_unitario
            pedido.total_a_pagar += subtotal
            pedido.save()

            messages.success(
                request, f"«{detalle.producto.nombre}» agregado al pedido."
            )

    return redirect("pedido_detalle", pk=pedido.pk)


@login_required
def eliminar_detalle(request, pedido_id, detalle_id):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        pedido = get_object_or_404(Pedido, pk=pedido_id)
    else:
        pedido = get_object_or_404(Pedido, pk=pedido_id, cliente__empresa=empresa)

    detalle = get_object_or_404(DetallePedido, pk=detalle_id, pedido=pedido)

    if request.method == "POST":
        subtotal = detalle.cantidad * detalle.precio_unitario
        pedido.total_a_pagar -= subtotal
        if pedido.total_a_pagar < 0:
            pedido.total_a_pagar = 0
        pedido.save()

        nombre_prod = detalle.producto.nombre
        detalle.delete()
        messages.success(request, f"«{nombre_prod}» eliminado del pedido.")

    return redirect("pedido_detalle", pk=pedido.pk)


@login_required
def pedido_eliminar(request, pk):
    empresa = obtener_empresa(request.user)

    if request.user.is_superuser:
        pedido = get_object_or_404(Pedido, pk=pk)
    else:
        if not empresa:
            messages.error(request, "No tienes una empresa asignada.")
            return redirect("dashboard")
        pedido = get_object_or_404(Pedido, pk=pk, cliente__empresa=empresa)

    if request.method == "POST":
        num_pedido = pedido.id
        pedido.delete()
        messages.success(request, f"Pedido #{num_pedido} eliminado.")
        return redirect("pedido_lista")

    return render(
        request,
        "ventas/eliminar.html",
        {
            "pedido": pedido,
        },
    )