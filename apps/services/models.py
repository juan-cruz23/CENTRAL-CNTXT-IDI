from decimal import Decimal

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


class Hardware(TimeStampedModel):
    """Equipo de cómputo/estación de trabajo. Fuente de costo de depreciación por hora."""

    name = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="nombre",
        help_text="Ej. 'Workstation Alta Gama'. Puede dejarse en blanco.",
    )
    value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor del equipo ($COP)",
    )
    depreciation_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="depreciación por hora ($COP)",
    )
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        ordering = ["-value"]
        verbose_name = "hardware"
        verbose_name_plural = "hardware"

    def __str__(self):
        return self.name or f"Hardware ${self.value:,.0f}"


class Software(TimeStampedModel):
    """Licencia de software. Fuente de costo de licencias por hora."""

    name = models.CharField(max_length=200, verbose_name="nombre")
    annual_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor anual ($COP)",
    )
    hourly_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="valor por hora ($COP)",
    )
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        ordering = ["name"]
        verbose_name = "software"
        verbose_name_plural = "software"

    def __str__(self):
        return self.name


class ServiceSubCategory(TimeStampedModel):
    """
    Sub categoría de servicio según estructura D.sign / V.sual.
    Ejemplos: 01 Urbanismo, 02 Edificación, 03 Complementario.
    """

    code = models.CharField(
        max_length=5,
        unique=True,
        verbose_name="código",
        help_text="Ej. '01', '02', '03'.",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
        help_text="Ej. 'Urbanismo', 'Edificación', 'Complementario'.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripción",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        ordering = ["code"]
        verbose_name = "sub categoría de servicio"
        verbose_name_plural = "sub categorías de servicio"

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
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
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
    # ── Pricing cascade inputs ───────────────────────────────────────────
    PRORRATEO_GASTOS_RATE = Decimal("27789")

    hourly_rate = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="honorarios/hora ($COP)",
    )
    hardware_cost_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="hardware depreciación/hora ($COP)",
    )
    software_cost_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="software licencias/hora ($COP)",
    )
    consumables_per_hour = models.DecimalField(
        max_digits=10, decimal_places=2, default=0,
        verbose_name="consumibles/hora ($COP)",
    )
    subcontracts = models.DecimalField(
        max_digits=14, decimal_places=2, default=0,
        verbose_name="subcontratos ($COP)",
    )
    contingency_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=15,
        verbose_name="desfase (%)",
    )
    utility_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=20,
        verbose_name="utilidad (%)",
    )
    negotiation_pct = models.DecimalField(
        max_digits=5, decimal_places=2, default=5,
        verbose_name="margen negociación (%)",
    )

    subcategory = models.ForeignKey(
        ServiceSubCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_templates",
        verbose_name="sub categor\u00eda",
    )
    responsible_role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="service_templates",
        verbose_name="rol responsable",
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

    # ── Pricing cascade (calculated, not stored) ─────────────────────────
    _Q = Decimal("0.01")

    @property
    def subtotal_honorarios(self) -> Decimal:
        return (self.hourly_rate * self.estimated_hours).quantize(self._Q)

    @property
    def hardware_total(self) -> Decimal:
        return (self.hardware_cost_per_hour * self.estimated_hours).quantize(self._Q)

    @property
    def software_total(self) -> Decimal:
        return (self.software_cost_per_hour * self.estimated_hours).quantize(self._Q)

    @property
    def consumables_total(self) -> Decimal:
        return (self.consumables_per_hour * self.estimated_hours).quantize(self._Q)

    @property
    def costo_directo(self) -> Decimal:
        return (self.subtotal_honorarios + self.hardware_total + self.software_total + self.consumables_total + self.subcontracts).quantize(self._Q)

    @property
    def prorrateo_gastos(self) -> Decimal:
        return (self.PRORRATEO_GASTOS_RATE * self.estimated_hours).quantize(self._Q)

    @property
    def costos_operacionales(self) -> Decimal:
        return (self.costo_directo + self.prorrateo_gastos).quantize(self._Q)

    @property
    def desfase_value(self) -> Decimal:
        return (self.costos_operacionales * self.contingency_pct / Decimal("100")).quantize(self._Q)

    @property
    def utility_value(self) -> Decimal:
        return ((self.costos_operacionales + self.desfase_value) * self.utility_pct / Decimal("100")).quantize(self._Q)

    @property
    def valor_neto(self) -> Decimal:
        return (self.costos_operacionales + self.desfase_value + self.utility_value).quantize(self._Q)

    @property
    def negotiation_value(self) -> Decimal:
        return (self.valor_neto * self.negotiation_pct / Decimal("100")).quantize(self._Q)

    @property
    def ica(self) -> Decimal:
        return (self.valor_neto * Decimal("0.00414")).quantize(self._Q)

    @property
    def gmf_4x1000(self) -> Decimal:
        return (self.valor_neto * Decimal("0.004")).quantize(self._Q)

    @property
    def valor_total_servicio(self) -> Decimal:
        return (self.valor_neto + self.negotiation_value + self.ica + self.gmf_4x1000).quantize(self._Q)


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


class Deliverable(TimeStampedModel):
    """
    Entregable asociado a una plantilla de servicio.
    Ejemplo: 'Modelo Tridimensional, Viewer 360 Escala Urbana' (unidad: Proyecto).
    """

    service_template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.CASCADE,
        related_name="deliverables",
        verbose_name="servicio",
    )
    name = models.CharField(
        max_length=400,
        verbose_name="nombre del entregable",
    )
    unit = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="unidad",
        help_text="Ej. Proyecto, 100m2, Und, 15 ha.",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="orden",
    )

    class Meta:
        ordering = ["service_template", "order", "name"]
        verbose_name = "entregable"
        verbose_name_plural = "entregables"

    def __str__(self):
        return f"{self.service_template.code} — {self.name}"


class KeyActivity(TimeStampedModel):
    """
    Actividad clave agrupadora dentro de un entregable.
    Ejemplo: 'Creación de topografía', 'Planteamiento Vial'.
    """

    deliverable = models.ForeignKey(
        Deliverable,
        on_delete=models.CASCADE,
        related_name="key_activities",
        verbose_name="entregable",
    )
    name = models.CharField(
        max_length=300,
        verbose_name="nombre",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="orden",
    )

    class Meta:
        ordering = ["deliverable", "order", "name"]
        verbose_name = "actividad clave"
        verbose_name_plural = "actividades clave"

    def __str__(self):
        return f"{self.deliverable.service_template.code} / {self.deliverable.name[:40]} — {self.name}"
