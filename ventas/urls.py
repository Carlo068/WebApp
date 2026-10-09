from django.urls import path
from . import views

urlpatterns = [
    path("", views.pedido_lista, name="pedido_lista"),
    path("nuevo/", views.pedido_crear, name="pedido_crear"),
    path("<int:pk>/", views.pedido_detalle, name="pedido_detalle"),
    path("<int:pedido_id>/agregar-producto/", views.agregar_detalle, name="agregar_detalle"),
    path("<int:pedido_id>/detalle/<int:detalle_id>/eliminar/", views.eliminar_detalle, name="eliminar_detalle"),
    path("<int:pedido_id>/pago/", views.registrar_pago, name="registrar_pago"),
    path("<int:pk>/eliminar/", views.pedido_eliminar, name="pedido_eliminar"),
]