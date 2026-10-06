import logging

from django.utils import timezone

from comun.clientes import ServicioNoDisponible, get_json

from .canales import get_canal
from .models import Notificacion, Plantilla

logger = logging.getLogger(__name__)


def contacto_asegurado(id_asegurado):
    """Consulta síncrona al Policyholder Service para obtener nombre y datos de contacto."""
    try:
        return get_json("POLICYHOLDER", f"/api/v1/asegurados/{id_asegurado}") or {}
    except ServicioNoDisponible as exc:
        # Sin URL configurada (modo aislado) se envía igual, sin datos de contacto.
        return {} if "no está configurada" in str(exc) else None


def asegurado_de_poliza(id_poliza):
    try:
        poliza = get_json("POLICY", f"/api/v1/polizas/{id_poliza}")
    except ServicioNoDisponible:
        return None
    return poliza.get("id_asegurado") if poliza else None


def enviar(id_asegurado, mensaje=None, codigo=None, canal=None, id_siniestro=None, variables=None):
    """Arma el mensaje (desde una plantilla o texto libre) y lo envía por el canal indicado."""
    plantilla = Plantilla.objects.filter(codigo=codigo).first() if codigo else None
    contacto = contacto_asegurado(id_asegurado)

    datos = dict(variables or {})
    if contacto:
        datos.setdefault("nombre", contacto.get("nombre", ""))

    canal = canal or (plantilla.canal if plantilla else "email")
    notificacion = Notificacion.objects.create(
        id_asegurado=id_asegurado,
        id_siniestro=id_siniestro,
        plantilla=plantilla,
        canal=canal,
        destinatario=(contacto or {}).get("telefono" if canal == "sms" else "email", ""),
        mensaje=plantilla.render(datos) if plantilla else (mensaje or ""),
    )

    if contacto is None:
        # El servicio de Asegurados está caído: no se pudo obtener el contacto.
        notificacion.status = Notificacion.FALLIDO
    else:
        try:
            ok = get_canal(canal).enviar(notificacion.destinatario, notificacion.mensaje)
        except Exception:
            logger.exception("error enviando notificación")
            ok = False
        notificacion.status = Notificacion.ENVIADO if ok else Notificacion.FALLIDO
        notificacion.sent_at = timezone.now() if ok else None

    notificacion.save()
    return notificacion
