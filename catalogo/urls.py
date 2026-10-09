from django.urls import path
from . import views

urlpatterns = [
    path("", views.producto_lista, name="producto_lista"),
    path("nuevo/", views.producto_nuevo, name="producto_nuevo"),
    path("<int:id>/editar/", views.producto_editar, name="producto_editar"),
    path("<int:id>/eliminar/", views.producto_eliminar, name="producto_eliminar"),
]