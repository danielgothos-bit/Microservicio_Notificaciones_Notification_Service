import uuid
from unittest import mock

from rest_framework.test import APITestCase

from comun.clientes import ServicioNoDisponible
from comun.eventos import INTERNAL_TOKEN

ASEGURADO = str(uuid.uuid4())
CONTACTO = {"id_asegurado": ASEGURADO, "nombre": "Ana", "email": "ana@example.com", "telefono": "3001234567"}


def get_json_falso(servicio, path, params=None):
    if servicio == "POLICYHOLDER":
        return CONTACTO
    if servicio == "POLICY":
        return {"id_asegurado": ASEGURADO}


@mock.patch("notificaciones.servicios.get_json", side_effect=get_json_falso)
class NotificacionesTests(APITestCase):
    def evento(self, nombre, data):
        return self.client.post("/api/v1/eventos", {"event": nombre, "data": data},
                                format="json", HTTP_X_INTERNAL_TOKEN=INTERNAL_TOKEN)

    def historial(self):
        return self.client.get(f"/api/v1/notificaciones/asegurado/{ASEGURADO}").data

    def test_plantillas_iniciales(self, get_json):
        codigos = [p["codigo"] for p in self.client.get("/api/v1/notificaciones/plantillas").data]
        self.assertIn("claim_opened", codigos)
        self.assertIn("payment_completed_indemnizacion", codigos)

    def test_claim_opened_notifica_con_plantilla(self, get_json):
        siniestro = str(uuid.uuid4())
        self.evento("claim.opened", {"id_siniestro": siniestro, "id_asegurado": ASEGURADO})

        [n] = self.historial()
        self.assertEqual(n["status"], "enviado")
        self.assertEqual(n["destinatario"], "ana@example.com")
        self.assertIn("Hola Ana", n["mensaje"])
        self.assertIn(siniestro, n["mensaje"])

    def test_pago_de_prima_busca_asegurado_en_polizas(self, get_json):
        self.evento("payment.completed", {"tipo": "prima", "id_poliza": str(uuid.uuid4()), "amount": "150000.00"})
        [n] = self.historial()
        self.assertEqual(n["codigo_plantilla"], "payment_completed_prima")
        self.assertIn("150000.00", n["mensaje"])

    def test_envio_manual(self, get_json):
        resp = self.client.post("/api/v1/notificaciones", {
            "id_asegurado": ASEGURADO, "mensaje": "Recordatorio de prueba", "canal": "sms",
        }, format="json")
        self.assertEqual(resp.status_code, 201)
        self.assertEqual(resp.data["destinatario"], "3001234567")

    def test_asegurados_caido_marca_fallido(self, get_json):
        get_json.side_effect = ServicioNoDisponible("Circuito abierto hacia POLICYHOLDER.")
        resp = self.client.post("/api/v1/notificaciones", {"id_asegurado": ASEGURADO, "mensaje": "x"}, format="json")
        self.assertEqual(resp.data["status"], "fallido")
