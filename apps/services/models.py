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
