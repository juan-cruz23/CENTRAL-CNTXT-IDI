from django.db import models

from apps.common.models import TimeStampedModel


class ProjectCategory(TimeStampedModel):
    """
    Categorizes projects by type.
    Examples: D3 - 'Vivienda Campestre', E1 - 'Edificios en Altura'.
    """

    code = models.CharField(
        max_length=10,
        unique=True,
        verbose_name="c\u00f3digo",
        help_text="Ej. 'D3', 'E1', 'P1'.",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
        help_text="Ej. 'Vivienda Campestre', 'Edificios en Altura'.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripci\u00f3n",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        verbose_name = "categor\u00eda de proyecto"
        verbose_name_plural = "categor\u00edas de proyecto"

    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectPhase(TimeStampedModel):
    """
    Represents a phase within a project lifecycle.
    Examples: Fase 1, Fase 2, Fase 3.
    """

    number = models.PositiveIntegerField(
        unique=True,
        verbose_name="n\u00famero",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
        help_text="Ej. 'Fase 1', 'Fase 2', 'Fase 3'.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripci\u00f3n",
    )

    class Meta:
        ordering = ["number"]
        verbose_name = "fase de proyecto"
        verbose_name_plural = "fases de proyecto"

    def __str__(self):
        return f"{self.number} - {self.name}"


class ServiceTemplate(TimeStampedModel):
    """
    Defines a reusable service template with pricing and effort estimates.
    Examples: D0.1, V1.2.
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="c\u00f3digo",
        help_text="Ej. 'D0.1', 'V1.2'.",
    )
    name = models.CharField(
        max_length=300,
        verbose_name="nombre",
    )
    category = models.ForeignKey(
        ProjectCategory,
        on_delete=models.CASCADE,
        related_name="service_templates",
        verbose_name="categor\u00eda",
    )
    phase = models.ForeignKey(
        ProjectPhase,
        on_delete=models.CASCADE,
        related_name="service_templates",
        verbose_name="fase",
    )
    base_unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="precio unitario base",
    )
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="horas estimadas",
    )
    estimated_days = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="d\u00edas estimados",
    )
    target_margin_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=20,
        verbose_name="margen objetivo (%)",
    )
    operative_line = models.ForeignKey(
        "organizations.OperativeLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_templates",
        verbose_name="l\u00ednea operativa",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripci\u00f3n",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        ordering = ["code"]
        verbose_name = "plantilla de servicio"
        verbose_name_plural = "plantillas de servicio"

    def __str__(self):
        return f"{self.code} - {self.name}"


class PricingChangeRequest(TimeStampedModel):
    """
    Request to change pricing/hours of a ServiceInstance.
    Used when a project leader (LP) needs to modify values
    that are restricted to Dirección Operativa (DO).
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "En Revisión"
        APPROVED = "APPROVED", "Aprobado"
        REJECTED = "REJECTED", "Rechazado"

    service_instance = models.ForeignKey(
        "projects.ServiceInstance",
        on_delete=models.CASCADE,
        related_name="pricing_requests",
        verbose_name="instancia de servicio",
    )
    requested_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="pricing_requests_made",
        verbose_name="solicitado por",
    )
    reviewed_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="pricing_requests_reviewed",
        verbose_name="revisado por",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="estado",
    )

    # Snapshot of current values
    current_unit_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name="precio unitario actual",
    )
    current_projected_hours = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        verbose_name="horas proyectadas actuales",
    )

    # Proposed values
    proposed_unit_price = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name="precio unitario propuesto",
    )
    proposed_projected_hours = models.DecimalField(
        max_digits=8, decimal_places=2, default=0,
        verbose_name="horas proyectadas propuestas",
    )

    justification = models.TextField(
        verbose_name="justificación",
    )
    review_notes = models.TextField(
        blank=True,
        verbose_name="notas de revisión",
    )
    reviewed_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name="fecha de revisión",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "solicitud de cambio de precio"
        verbose_name_plural = "solicitudes de cambio de precio"

    def __str__(self):
        return f"PCR-{self.pk} ({self.service_instance.code}) - {self.get_status_display()}"


class ServiceActivity(TimeStampedModel):
    """
    Represents an individual activity within a service template.
    """

    service_template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="plantilla de servicio",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="orden",
    )
    name = models.CharField(
        max_length=300,
        verbose_name="nombre",
    )
    responsible_role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_activities",
        verbose_name="rol responsable",
    )
    estimated_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="horas estimadas",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripci\u00f3n",
    )

    class Meta:
        ordering = ["service_template", "order"]
        verbose_name = "actividad de servicio"
        verbose_name_plural = "actividades de servicio"

    def __str__(self):
        return f"{self.service_template.code} - {self.order}. {self.name}"
