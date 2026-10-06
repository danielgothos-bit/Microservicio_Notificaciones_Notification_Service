from rest_framework import serializers

from .models import CANALES, Notificacion, Plantilla


class PlantillaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plantilla
        fields = ["id_plantilla", "codigo", "canal", "cuerpo_plantilla"]
        read_only_fields = ["id_plantilla"]


class NotificacionSerializer(serializers.ModelSerializer):
    codigo_plantilla = serializers.CharField(source="plantilla.codigo", read_only=True, default=None)

    class Meta:
        model = Notificacion
        fields = [
            "id_notificacion",
            "id_asegurado",
            "id_siniestro",
            "codigo_plantilla",
            "canal",
            "destinatario",
            "mensaje",
            "status",
            "sent_at",
        ]


class EnviarSerializer(serializers.Serializer):
    id_asegurado = serializers.UUIDField()
    id_siniestro = serializers.UUIDField(required=False, allow_null=True)
    codigo_plantilla = serializers.SlugRelatedField(slug_field="codigo", queryset=Plantilla.objects.all(), required=False)
    mensaje = serializers.CharField(required=False)
    canal = serializers.ChoiceField(choices=[c for c, _ in CANALES], required=False)
    variables = serializers.DictField(required=False)

    def validate(self, data):
        if not data.get("codigo_plantilla") and not data.get("mensaje"):
            raise serializers.ValidationError("Envía un `mensaje` o un `codigo_plantilla`.")
        return data
