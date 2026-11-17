"""Pruebas unitarias: una unidad de lógica de negocio aislada; las dependencias externas se simulan con mocks."""
import uuid
from unittest import mock

from django.test import TestCase

from notificaciones.models import Notificacion, Plantilla
from notificaciones.servicios import enviar


class NotificacionesUnitTests(TestCase):
    @mock.patch("notificaciones.servicios.get_json", return_value={"nombre": "Laura", "email": "laura@example.com", "telefono": "300"})
    def test_usa_plantilla_y_datos_del_asegurado(self, get_json):
        Plantilla.objects.create(codigo="prueba_unitaria", canal="email", cuerpo_plantilla="Hola {nombre}, tu caso {caso} avanza.")
        n = enviar(uuid.uuid4(), codigo="prueba_unitaria", variables={"caso": "SN-1"})
        self.assertEqual(n.mensaje, "Hola Laura, tu caso SN-1 avanza.")
        self.assertEqual(n.status, Notificacion.ENVIADO)

    @mock.patch("notificaciones.servicios.get_canal")
    @mock.patch("notificaciones.servicios.get_json", return_value={"nombre": "Laura", "telefono": "300"})
    def test_si_el_canal_falla_queda_como_fallida(self, get_json, get_canal):
        get_canal.return_value.enviar.side_effect = RuntimeError("proveedor SMS caído")
        n = enviar(uuid.uuid4(), mensaje="Prueba", canal="sms")
        self.assertEqual(n.status, Notificacion.FALLIDO)
