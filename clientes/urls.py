from django.urls import path

from . import views

urlpatterns = [
    path("", views.cliente_lista, name="cliente_lista"),
    path("nuevo/", views.cliente_nuevo, name="cliente_nuevo"),
    path("editar/<int:id>/", views.cliente_editar, name="cliente_editar"),
    path("eliminar/<int:id>/", views.cliente_eliminar, name="cliente_eliminar"),
]