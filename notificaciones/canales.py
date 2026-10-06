"""
Adaptadores de canal de envío (todos con la misma interfaz, sección 2.4).

Por defecto el envío es simulado (se registra en el log). Si se configura EMAIL_HOST,
las notificaciones por email se envían de verdad por SMTP con Django.
"""
import logging
import os

from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class CanalSimulado:
    def enviar(self, destinatario, mensaje):
        logger.info("notificación enviada (simulada)", extra={"destinatario": destinatario, "mensaje": mensaje})
        return True


class CanalEmail:
    def enviar(self, destinatario, mensaje):
        if not destinatario:
            return False
        send_mail("InsureFlow", mensaje, os.getenv("EMAIL_FROM", "no-reply@insureflow.co"), [destinatario])
        return True


def get_canal(canal):
    if canal == "email" and os.getenv("EMAIL_HOST"):
        return CanalEmail()
    return CanalSimulado()
