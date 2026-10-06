from django.urls import path

from . import views

urlpatterns = [
    path("api/v1/notificaciones", views.notificaciones),
    path("api/v1/notificaciones/asegurado/<uuid:id>", views.notificaciones_por_asegurado),
    path("api/v1/notificaciones/plantillas", views.plantillas),
]
