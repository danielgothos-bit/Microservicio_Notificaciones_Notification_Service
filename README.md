# Microservicio de Notificaciones — Notification Service

Microservicio de InsureFlow definido en la sección 4.7 del documento de arquitectura.

## Responsabilidad

Informar a los asegurados sobre el avance de su siniestro, sus pólizas y sus pagos, usando plantillas por canal (email, sms, push, app).

## Tecnología

Python · Django REST Framework · PostgreSQL (`notification_db`) · Celery + Redis · Docker

## Modelo de datos (3FN, IDs UUID)

`plantilla` (código único, 10 plantillas iniciales) y `notificacion`.

## Endpoints

```
POST /api/v1/notificaciones — enviar notificación (mensaje libre o `codigo_plantilla`)
GET  /api/v1/notificaciones/asegurado/{id} — historial de notificaciones
GET/POST /api/v1/notificaciones/plantillas — plantillas
GET  /health — estado del servicio y de su base de datos
POST /api/v1/eventos — endpoint interno donde otros microservicios entregan eventos
```

## Eventos

Publica:
- (ninguno)

Consume:
- claim.opened
- claim.documentation_requested
- claim.rejected
- policy.issued
- policy.renewed
- policy.cancelled
- payment.completed
- payment.failed

Los eventos se encolan con Celery/Redis y se entregan por HTTP al endpoint `/api/v1/eventos` de cada
suscriptor, con reintentos y backoff exponencial (módulo `comun/eventos.py`). Cada evento se procesa una
sola vez (idempotencia por `event_id`).

## Variables de entorno

- `DATABASE_URL`, `REDIS_URL`: base de datos y Redis propios
- `INTERNAL_TOKEN`: token compartido por todos los microservicios para los eventos
- `RUN_WORKER_IN_WEB=1`: corre el worker de Celery dentro del mismo contenedor (Render gratis)
- `SYNC_TIMEOUT`: timeout de las llamadas REST síncronas (3 s por defecto)
- `POLICYHOLDER_SERVICE_URL`: microservicio de Asegurados
- `POLICY_SERVICE_URL`: microservicio de Pólizas

Si una URL no está configurada, el servicio funciona en modo aislado (omite esa validación o ese evento).

## Ejecución local

```bash
docker compose up --build
```

El servicio queda en http://localhost:8006 y las migraciones se aplican solas al arrancar.

Pruebas:

```bash
docker compose exec notification_service python manage.py test notificaciones
```

## Despliegue en Render

En Render: **New → Blueprint** → conectar este repositorio → **Deploy Blueprint**.
El `render.yaml` crea el servicio web, su PostgreSQL y su Redis (plan gratis).
