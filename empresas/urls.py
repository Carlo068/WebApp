from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path("", views.dashboard, name="dashboard"),

    # Autenticación
    path(
        "login/",
        auth_views.LoginView.as_view(
            template_name="registration/login.html"
        ),
        name="login",
    ),
    path(
        "logout/",
        auth_views.LogoutView.as_view(next_page="login"),
        name="logout",
    ),

    # CRUD de Empresas
    path("empresas/",views.empresa_lista,name="empresa_lista",),
    path("empresas/nuevo/",views.empresa_nueva,name="empresa_nueva"),
    path("empresas/<int:id>/editar/",views.empresa_editar,name="empresa_editar"),
    path("empresas/<int:id>/eliminar/",views.empresa_eliminar,name="empresa_eliminar"),
]