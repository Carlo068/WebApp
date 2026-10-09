from django.contrib import admin

from .models import Empleado, Empresa

admin.site.register(Empresa)
admin.site.register(Empleado)