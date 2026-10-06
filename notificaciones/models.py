import uuid
from collections import defaultdict

from django.db import models
from django.db.models import Q

CANALES = [("email", "Email"), ("sms", "SMS"), ("push", "Push"), ("app", "App")]


class Plantilla(models.Model):
    id_plantilla = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    codigo = models.CharField(max_length=60, unique=True)
    canal = models.CharField(max_length=10, choices=CANALES)
    cuerpo_plantilla = models.TextField()  # texto con variables entre llaves, ej: {nombre}

    class Meta:
        db_table = "plantilla"
        constraints = [
            models.CheckConstraint(condition=Q(canal__in=["email", "sms", "push", "app"]), name="chk_plantilla_canal"),
        ]

    def render(self, variables):
        return self.cuerpo_plantilla.format_map(defaultdict(str, variables))

    def __str__(self):
        return self.codigo


class Notificacion(models.Model):
    PENDIENTE, ENVIADO, FALLIDO = "pendiente", "enviado", "fallido"
    STATUS_CHOICES = [(PENDIENTE, "Pendiente"), (ENVIADO, "Enviado"), (FALLIDO, "Fallido")]

    id_notificacion = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    id_asegurado = models.UUIDField()  # FK-ext -> Policyholder Service
    id_siniestro = models.UUIDField(blank=True, null=True)  # FK-ext -> Claims Service
    plantilla = models.ForeignKey(Plantilla, on_delete=models.SET_NULL, blank=True, null=True,
                                  related_name="notificaciones", db_column="id_plantilla")
    canal = models.CharField(max_length=10, choices=CANALES)
    destinatario = models.CharField(max_length=255, blank=True)
    mensaje = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=PENDIENTE)
    sent_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = "notificacion"
        indexes = [
            models.Index(fields=["id_asegurado"], name="idx_notificacion_asegurado"),
            models.Index(fields=["sent_at"], name="idx_notificacion_sent_at"),
            models.Index(fields=["status"], name="idx_notificacion_status"),
        ]
        constraints = [
            models.CheckConstraint(condition=Q(canal__in=["email", "sms", "push", "app"]), name="chk_notificacion_canal"),
            models.CheckConstraint(condition=Q(status__in=["pendiente", "enviado", "fallido"]), name="chk_notificacion_status"),
        ]
