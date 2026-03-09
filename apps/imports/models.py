from django.db import models

from apps.common.models import TimeStampedModel


class ImportJob(TimeStampedModel):
    """
    Tracks a CSV import job through its lifecycle: upload, preview,
    confirmation and execution.
    """

    class SourceType(models.TextChoices):
        COR_SHEET = "COR_SHEET", "C.O.R. Data Proyectos"
        FINANCIAL = "FINANCIAL", "Control Financiero"
        HOLIDAYS = "HOLIDAYS", "Festivos"
        LOGGRO_ACCOUNTING = "LOGGRO_ACCOUNTING", "Auxiliar Contable Loggro"

    class Status(models.TextChoices):
        UPLOADED = "UPLOADED", "Subido"
        PREVIEWED = "PREVIEWED", "Previsualizado"
        CONFIRMED = "CONFIRMED", "Confirmado"
        COMPLETED = "COMPLETED", "Completado"
        FAILED = "FAILED", "Fallido"

    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="import_jobs",
        verbose_name="subido por",
    )
    file = models.FileField(
        upload_to="imports/%Y/%m/",
        verbose_name="archivo",
    )
    source_type = models.CharField(
        max_length=30,
        choices=SourceType.choices,
        verbose_name="tipo de fuente",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.UPLOADED,
        verbose_name="estado",
    )
    records_total = models.IntegerField(
        default=0,
        verbose_name="registros totales",
    )
    records_imported = models.IntegerField(
        default=0,
        verbose_name="registros importados",
    )
    records_failed = models.IntegerField(
        default=0,
        verbose_name="registros fallidos",
    )
    errors = models.JSONField(
        default=list,
        blank=True,
        verbose_name="errores",
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="completado en",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "trabajo de importación"
        verbose_name_plural = "trabajos de importación"

    def __str__(self):
        return (
            f"Import #{self.pk} - {self.get_source_type_display()} "
            f"({self.get_status_display()})"
        )
