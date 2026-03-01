from django.db import models

from apps.common.models import TimeStampedModel


# ---------------------------------------------------------------------------
# TeamMemberCapacity
# ---------------------------------------------------------------------------
class TeamMemberCapacity(TimeStampedModel):
    """Tracks the weekly available hours for a team member over a given period."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="capacities",
        verbose_name="usuario",
    )
    weekly_available_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=40,
        verbose_name="horas disponibles por semana",
    )
    effective_from = models.DateField(
        verbose_name="vigente desde",
    )
    effective_until = models.DateField(
        null=True,
        blank=True,
        verbose_name="vigente hasta",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["user", "effective_from"]
        verbose_name = "capacidad de miembro"
        verbose_name_plural = "capacidades de miembros"

    def __str__(self):
        return f"{self.user} - {self.weekly_available_hours}h ({self.effective_from})"


# ---------------------------------------------------------------------------
# ProjectAllocation
# ---------------------------------------------------------------------------
class ProjectAllocation(TimeStampedModel):
    """Tracks how many hours/percentage a user is allocated to a project."""

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="usuario",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="proyecto",
    )
    role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="rol",
    )
    start_date = models.DateField(
        verbose_name="fecha de inicio",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de fin",
    )
    weekly_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="horas semanales",
    )
    allocation_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="porcentaje de asignación",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["user", "start_date"]
        verbose_name = "asignación de proyecto"
        verbose_name_plural = "asignaciones de proyecto"

    def __str__(self):
        return f"{self.user} -> {self.project} ({self.allocation_pct}%)"


# ---------------------------------------------------------------------------
# CapacityAlert
# ---------------------------------------------------------------------------
class CapacityAlert(TimeStampedModel):
    """Alerts generated when capacity thresholds are breached."""

    class AlertType(models.TextChoices):
        OVERLOAD = "OVERLOAD", "Sobrecarga"
        UNDERLOAD = "UNDERLOAD", "Subcarga"
        CONFLICT = "CONFLICT", "Conflicto"

    user = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="capacity_alerts",
        verbose_name="usuario",
    )
    alert_type = models.CharField(
        max_length=20,
        choices=AlertType.choices,
        verbose_name="tipo de alerta",
    )
    week_start = models.DateField(
        verbose_name="inicio de semana",
    )
    allocated_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="horas asignadas",
    )
    available_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="horas disponibles",
    )
    details = models.TextField(
        blank=True,
        verbose_name="detalles",
    )
    is_resolved = models.BooleanField(
        default=False,
        verbose_name="resuelta",
    )

    class Meta:
        ordering = ["-week_start"]
        verbose_name = "alerta de capacidad"
        verbose_name_plural = "alertas de capacidad"

    def __str__(self):
        return f"{self.user} - {self.alert_type} ({self.week_start})"
