from django.conf import settings
from django.db import models


class TimeStampedModel(models.Model):
    """Abstract base model that provides self-updating created_at and updated_at fields."""

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditLog(models.Model):
    """Tracks create, update, and delete operations on models."""

    class Action(models.TextChoices):
        CREATE = "CREATE", "Crear"
        UPDATE = "UPDATE", "Actualizar"
        DELETE = "DELETE", "Eliminar"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="audit_logs",
        verbose_name="usuario",
    )
    action = models.CharField(
        max_length=10,
        choices=Action.choices,
        verbose_name="acción",
    )
    model_name = models.CharField(
        max_length=255,
        verbose_name="nombre del modelo",
    )
    object_id = models.CharField(
        max_length=255,
        verbose_name="ID del objeto",
    )
    changes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name="cambios",
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="fecha y hora",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name="dirección IP",
    )

    class Meta:
        verbose_name = "registro de auditoría"
        verbose_name_plural = "registros de auditoría"
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} - {self.model_name} ({self.object_id}) - {self.timestamp}"
