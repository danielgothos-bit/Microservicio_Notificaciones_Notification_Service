from django.db import migrations

PLANTILLAS = [
    ("claim_opened", "email",
     "Hola {nombre}, recibimos el reporte de tu siniestro {id_siniestro}. "
     "Un perito será asignado y te mantendremos informado del avance."),
    ("documentation_requested", "email",
     "Hola {nombre}, para continuar con tu siniestro {id_siniestro} necesitamos documentación adicional. "
     "Por favor cárgala en el portal de asegurados."),
    ("claim_rejected", "email",
     "Hola {nombre}, tu siniestro {id_siniestro} fue revisado y no fue aprobado. "
     "Puedes comunicarte con tu agente para más información."),
    ("policy_issued", "email",
     "Hola {nombre}, tu póliza de {product_type} {id_poliza} fue emitida. "
     "Vigencia: {effective_date} a {expiry_date}. Te recordaremos antes del vencimiento."),
    ("policy_renewed", "email",
     "Hola {nombre}, tu póliza {id_poliza} fue renovada. Nueva fecha de vencimiento: {expiry_date}."),
    ("policy_cancelled", "email",
     "Hola {nombre}, tu póliza {id_poliza} fue cancelada."),
    ("payment_completed_prima", "email",
     "Hola {nombre}, recibimos el pago de la prima de tu póliza {id_poliza} por ${amount}. ¡Gracias!"),
    ("payment_completed_indemnizacion", "email",
     "Hola {nombre}, el pago de la indemnización de tu siniestro {id_siniestro} por ${amount} fue realizado."),
    ("payment_failed", "email",
     "Hola {nombre}, tuvimos un inconveniente procesando el pago de {tipo}. "
     "Nuestro equipo lo está revisando y te contactaremos pronto."),
    ("vencimiento_poliza", "sms",
     "InsureFlow: {nombre}, tu póliza {id_poliza} vence el {expiry_date}. Renuévala para mantener tu cobertura."),
]


def crear(apps, schema_editor):
    Plantilla = apps.get_model("notificaciones", "Plantilla")
    for codigo, canal, cuerpo in PLANTILLAS:
        Plantilla.objects.update_or_create(codigo=codigo, defaults={"canal": canal, "cuerpo_plantilla": cuerpo})


def borrar(apps, schema_editor):
    apps.get_model("notificaciones", "Plantilla").objects.filter(codigo__in=[p[0] for p in PLANTILLAS]).delete()


class Migration(migrations.Migration):
    dependencies = [("notificaciones", "0001_initial")]
    operations = [migrations.RunPython(crear, borrar)]
