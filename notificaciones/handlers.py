"""
Eventos que consume el microservicio de Notificaciones (sección 4.7).
Cada evento se traduce en una notificación al asegurado usando una plantilla.
"""
import logging

from .servicios import asegurado_de_poliza, enviar

logger = logging.getLogger(__name__)


def _notificar(codigo, data, **variables):
    id_asegurado = data.get("id_asegurado")
    if not id_asegurado and data.get("id_poliza"):
        id_asegurado = asegurado_de_poliza(data["id_poliza"])
    if not id_asegurado:
        logger.warning("no se pudo identificar al asegurado", extra={"codigo": codigo})
        return
    enviar(id_asegurado, codigo=codigo, id_siniestro=data.get("id_siniestro"),
           variables={**{k: v for k, v in data.items() if v is not None}, **variables})


def on_claim_opened(data):
    _notificar("claim_opened", data)


def on_documentation_requested(data):
    _notificar("documentation_requested", data)


def on_claim_rejected(data):
    _notificar("claim_rejected", data)


def on_policy_issued(data):
    _notificar("policy_issued", data)


def on_policy_renewed(data):
    _notificar("policy_renewed", data)


def on_policy_cancelled(data):
    _notificar("policy_cancelled", data)


def on_payment_completed(data):
    _notificar("payment_completed_" + ("indemnizacion" if data.get("tipo") == "indemnizacion" else "prima"), data)


def on_payment_failed(data):
    _notificar("payment_failed", data)


HANDLERS = {
    "claim.opened": on_claim_opened,
    "claim.documentation_requested": on_documentation_requested,
    "claim.rejected": on_claim_rejected,
    "policy.issued": on_policy_issued,
    "policy.renewed": on_policy_renewed,
    "policy.cancelled": on_policy_cancelled,
    "payment.completed": on_payment_completed,
    "payment.failed": on_payment_failed,
}
