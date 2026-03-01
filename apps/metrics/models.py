from django.db import models

from apps.common.models import TimeStampedModel


class ProjectMetricSnapshot(TimeStampedModel):
    """
    Point-in-time snapshot of Earned Value Management (EVM) metrics
    and financial indicators for a project.

    Each snapshot captures the project's performance state on a given date,
    enabling historical trend analysis and S-Curve generation.
    """

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="metric_snapshots",
        verbose_name="proyecto",
    )
    snapshot_date = models.DateField(
        verbose_name="fecha de snapshot",
    )

    # ------------------------------------------------------------------
    # EVM Core
    # ------------------------------------------------------------------
    bac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="BAC",
        help_text="Budget at Completion (= project total_value).",
    )
    planned_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="PV",
        help_text="Planned Value = SUM(service.total_value * service.expected_progress_pct / 100).",
    )
    earned_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="EV",
        help_text="Earned Value = SUM(service.total_value * service.progress_pct / 100).",
    )
    actual_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="AC",
        help_text="Actual Cost = SUM(service.real_operative_cost).",
    )

    # ------------------------------------------------------------------
    # Performance Indices
    # ------------------------------------------------------------------
    spi = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        verbose_name="SPI",
        help_text="Schedule Performance Index = EV / PV.",
    )
    cpi = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        verbose_name="CPI",
        help_text="Cost Performance Index = EV / AC.",
    )

    # ------------------------------------------------------------------
    # Variances
    # ------------------------------------------------------------------
    schedule_variance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="SV",
        help_text="Schedule Variance = EV - PV.",
    )
    cost_variance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="CV",
        help_text="Cost Variance = EV - AC.",
    )

    # ------------------------------------------------------------------
    # Forecasts
    # ------------------------------------------------------------------
    eac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="EAC",
        help_text="Estimate at Completion = BAC / CPI.",
    )
    etc = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="ETC",
        help_text="Estimate to Complete = EAC - AC.",
    )
    vac = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="VAC",
        help_text="Variance at Completion = BAC - EAC.",
    )

    # ------------------------------------------------------------------
    # Progress
    # ------------------------------------------------------------------
    overall_progress_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="avance general (%)",
    )
    expected_progress_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="avance esperado (%)",
    )
    schedule_deviation_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="desviación de cronograma (%)",
    )

    # ------------------------------------------------------------------
    # Financial
    # ------------------------------------------------------------------
    total_revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="ingresos totales",
    )
    total_costs = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costos totales",
    )
    projected_margin_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="margen proyectado (%)",
    )

    class Meta:
        ordering = ["-snapshot_date"]
        unique_together = ("project", "snapshot_date")
        indexes = [
            models.Index(
                fields=["project", "snapshot_date"],
                name="idx_metric_proj_date",
            ),
        ]
        verbose_name = "snapshot de métricas"
        verbose_name_plural = "snapshots de métricas"

    def __str__(self):
        return f"{self.project} - {self.snapshot_date}"
