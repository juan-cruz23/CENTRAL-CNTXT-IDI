from django.db import models

from apps.common.models import TimeStampedModel


class RFI(TimeStampedModel):
    """Solicitud de informacion (Request for Information) asociada a un proyecto."""

    class Status(models.TextChoices):
        OPEN = "OPEN", "Abierto"
        IN_PROGRESS = "IN_PROGRESS", "En progreso"
        RESOLVED = "RESOLVED", "Resuelto"
        CLOSED = "CLOSED", "Cerrado"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="rfis",
        verbose_name="proyecto",
    )
    service_instance = models.ForeignKey(
        "projects.ServiceInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rfis",
        verbose_name="instancia de servicio",
    )
    code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="codigo",
    )
    observations = models.TextField(
        blank=True,
        verbose_name="observaciones",
    )
    time_invested_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="horas invertidas",
    )
    professional = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="rfis",
        verbose_name="profesional",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name="estado",
    )
    external_discipline = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="disciplina externa",
    )
    response = models.TextField(
        blank=True,
        verbose_name="respuesta",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "RFI"
        verbose_name_plural = "RFIs"

    def __str__(self):
        return f"RFI {self.code} - {self.project}"
