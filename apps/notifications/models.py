from django.db import models

from apps.common.models import TimeStampedModel


class Alert(TimeStampedModel):
    """System-wide alert/notification model for projects and users."""

    class Severity(models.TextChoices):
        INFO = "INFO", "Información"
        WARNING = "WARNING", "Advertencia"
        CRITICAL = "CRITICAL", "Crítico"

    class Category(models.TextChoices):
        SCHEDULE_DEVIATION = "SCHEDULE_DEVIATION", "Desviación de cronograma"
        COST_OVERRUN = "COST_OVERRUN", "Sobrecosto"
        CAPACITY_OVERLOAD = "CAPACITY_OVERLOAD", "Sobrecarga de capacidad"
        PAYMENT_OVERDUE = "PAYMENT_OVERDUE", "Pago vencido"
        MILESTONE_DUE = "MILESTONE_DUE", "Hito próximo"
        SATISFACTION_LOW = "SATISFACTION_LOW", "Satisfacción baja"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="alerts",
        null=True,
        blank=True,
        verbose_name="proyecto",
    )
    severity = models.CharField(
        max_length=20,
        choices=Severity.choices,
        default=Severity.INFO,
        verbose_name="severidad",
    )
    category = models.CharField(
        max_length=50,
        choices=Category.choices,
        verbose_name="categoría",
    )
    title = models.CharField(
        max_length=300,
        verbose_name="título",
    )
    message = models.TextField(
        verbose_name="mensaje",
    )
    target_users = models.ManyToManyField(
        "accounts.User",
        related_name="alerts",
        blank=True,
        verbose_name="usuarios destinatarios",
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name="leída",
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name="resuelta",
    )
    resolved_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="fecha de resolución",
    )
    resolved_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="resolved_alerts",
        verbose_name="resuelta por",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "alerta"
        verbose_name_plural = "alertas"

    def __str__(self):
        return f"[{self.severity}] {self.title}"
