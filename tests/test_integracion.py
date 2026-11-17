"""Prueba de integración: endpoint + lógica de negocio + base de datos funcionando juntos."""
import uuid
from unittest import mock

from rest_framework.test import APITestCase

from notificaciones.models import Notificacion


@mock.patch("notificaciones.servicios.get_json", return_value={"nombre": "Ana", "email": "ana@example.com"})
class NotificacionesIntegracionTests(APITestCase):
    def test_enviar_y_consultar_historial_del_asegurado(self, get_json):
        aseg = str(uuid.uuid4())
        resp = self.client.post("/api/v1/notificaciones", {"id_asegurado": aseg, "mensaje": "Tu póliza fue emitida", "canal": "email"},
                                format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertTrue(Notificacion.objects.filter(id_asegurado=aseg).exists())
        self.assertEqual(len(self.client.get(f"/api/v1/notificaciones/asegurado/{aseg}").data), 1)
