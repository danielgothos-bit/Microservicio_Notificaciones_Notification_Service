from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Notificacion, Plantilla
from .serializers import EnviarSerializer, NotificacionSerializer, PlantillaSerializer
from .servicios import enviar


@api_view(["POST"])
def notificaciones(request):
    serializer = EnviarSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    datos = serializer.validated_data
    plantilla = datos.get("codigo_plantilla")

    notificacion = enviar(
        datos["id_asegurado"],
        mensaje=datos.get("mensaje"),
        codigo=plantilla.codigo if plantilla else None,
        canal=datos.get("canal"),
        id_siniestro=datos.get("id_siniestro"),
        variables=datos.get("variables"),
    )
    return Response(NotificacionSerializer(notificacion).data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def notificaciones_por_asegurado(request, id):
    qs = Notificacion.objects.filter(id_asegurado=id).select_related("plantilla").order_by("-sent_at")
    return Response(NotificacionSerializer(qs, many=True).data)


@api_view(["GET", "POST"])
def plantillas(request):
    if request.method == "GET":
        return Response(PlantillaSerializer(Plantilla.objects.order_by("codigo"), many=True).data)

    serializer = PlantillaSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data, status=status.HTTP_201_CREATED)
