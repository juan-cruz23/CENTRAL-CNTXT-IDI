from decimal import Decimal
from functools import cached_property

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
    operative_line = models.ForeignKey(
        "organizations.OperativeLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="project_categories",
        verbose_name="l\u00ednea operativa",
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
    brand = models.CharField(max_length=100, blank=True, verbose_name="marca")
    model_name = models.CharField(max_length=100, blank=True, verbose_name="modelo")
    serial_number = models.CharField(max_length=100, blank=True, verbose_name="número de serie")
    location = models.CharField(max_length=200, blank=True, verbose_name="ubicación")
    value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor del equipo ($COP)",
    )
    depreciation_years = models.PositiveSmallIntegerField(
        default=5,
        verbose_name="años de depreciación",
    )
    depreciation_per_hour = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="depreciación por hora ($COP)",
    )
    purchase_date = models.DateField(null=True, blank=True, verbose_name="fecha de compra")
    warranty_expiration = models.DateField(null=True, blank=True, verbose_name="garantía hasta")
    is_direct_cost = models.BooleanField(default=True, verbose_name="costo directo")
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        ordering = ["-value"]
        verbose_name = "hardware"
        verbose_name_plural = "hardware"

    # Horas anuales productivas (52 semanas × 40 h/sem)
    ANNUAL_HOURS = Decimal("2080")

    @property
    def warranty_days_left(self):
        if not self.warranty_expiration:
            return None
        from django.utils import timezone
        return (self.warranty_expiration - timezone.now().date()).days

    def save(self, *args, **kwargs):
        # Auto-calcular depreciation_per_hour = value / depreciation_years / ANNUAL_HOURS
        if self.value and self.depreciation_years and self.depreciation_years > 0:
            self.depreciation_per_hour = (
                Decimal(str(self.value))
                / Decimal(str(self.depreciation_years))
                / self.ANNUAL_HOURS
            ).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or f"Hardware ${self.value:,.0f}"


class HardwareMaintenance(TimeStampedModel):
    """Registro de mantenimiento de un equipo."""

    TYPE_CHOICES = [
        ("preventivo", "Preventivo"),
        ("correctivo", "Correctivo"),
        ("garantia", "Garantía"),
    ]

    hardware = models.ForeignKey(
        Hardware,
        on_delete=models.CASCADE,
        related_name="maintenances",
        verbose_name="equipo",
    )
    maintenance_type = models.CharField(
        max_length=20,
        choices=TYPE_CHOICES,
        default="preventivo",
        verbose_name="tipo",
    )
    date = models.DateField(verbose_name="fecha")
    cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costo ($COP)",
    )
    provider = models.CharField(max_length=200, blank=True, verbose_name="proveedor / técnico")
    description = models.TextField(blank=True, verbose_name="descripción")
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name="próximo mantenimiento")

    class Meta:
        ordering = ["-date"]
        verbose_name = "mantenimiento"
        verbose_name_plural = "mantenimientos"

    def __str__(self):
        return f"{self.hardware} — {self.get_maintenance_type_display()} {self.date}"


class Software(TimeStampedModel):
    """Licencia de software. Fuente de costo de licencias por hora."""

    LICENSE_TYPE_CHOICES = [
        ("perpetua", "Perpetua"),
        ("suscripcion", "Suscripción"),
        ("por_usuario", "Por usuario"),
    ]

    name = models.CharField(max_length=200, verbose_name="nombre")
    vendor = models.CharField(max_length=200, blank=True, verbose_name="proveedor")
    version = models.CharField(max_length=100, blank=True, verbose_name="versión")
    license_type = models.CharField(
        max_length=20,
        choices=LICENSE_TYPE_CHOICES,
        default="suscripcion",
        verbose_name="tipo de licencia",
    )
    seats = models.PositiveSmallIntegerField(default=1, verbose_name="cantidad de puestos")
    annual_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor anual ($COP)",
    )
    monthly_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor mensual ($COP)",
    )
    hourly_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="valor por hora ($COP)",
    )
    acquisition_date = models.DateField(null=True, blank=True, verbose_name="fecha de adquisición")
    expiration_date = models.DateField(null=True, blank=True, verbose_name="fecha de vencimiento")
    auto_renewal = models.BooleanField(default=False, verbose_name="renovación automática")
    is_direct_cost = models.BooleanField(default=True, verbose_name="costo directo")
    vendor_url = models.URLField(blank=True, verbose_name="URL del proveedor")
    notes = models.TextField(blank=True, verbose_name="notas")
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        ordering = ["name"]
        verbose_name = "software"
        verbose_name_plural = "software"

    ANNUAL_HOURS = Decimal("2080")  # 52 semanas × 40 h/sem

    @property
    def days_to_expiration(self):
        if not self.expiration_date:
            return None
        from django.utils import timezone
        return (self.expiration_date - timezone.now().date()).days

    def save(self, *args, **kwargs):
        # Auto-calcular hourly_value desde annual_value (o monthly × 12)
        annual = self.annual_value or (
            Decimal(str(self.monthly_value)) * Decimal("12") if self.monthly_value else Decimal("0")
        )
        if annual and annual > 0:
            self.hourly_value = (
                Decimal(str(annual)) / self.ANNUAL_HOURS
            ).quantize(Decimal("0.01"))
            # Sincronizar también annual_value si solo se ingresó monthly_value
            if not self.annual_value and self.monthly_value:
                self.annual_value = (Decimal(str(self.monthly_value)) * Decimal("12")).quantize(Decimal("0.01"))
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SoftwarePayment(TimeStampedModel):
    """Registro de un pago de licencia de software."""

    software = models.ForeignKey(
        Software,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="software",
    )
    payment_date = models.DateField(verbose_name="fecha de pago")
    amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        verbose_name="valor pagado ($COP)",
    )
    notes = models.CharField(max_length=300, blank=True, verbose_name="notas")

    class Meta:
        ordering = ["-payment_date"]
        verbose_name = "pago de software"
        verbose_name_plural = "pagos de software"

    def __str__(self):
        return f"{self.software.name} — {self.payment_date} — ${self.amount:,.0f}"


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
    operative_line = models.ForeignKey(
        "organizations.OperativeLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="subcategories",
        verbose_name="línea operativa",
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
    hardwares = models.ManyToManyField(
        "Hardware",
        blank=True,
        related_name="service_templates_using",
        verbose_name="hardware aplicable",
        help_text="Hardware que aplica a este servicio. La depreciación/hora se autocalcula de la suma.",
    )
    softwares = models.ManyToManyField(
        "Software",
        blank=True,
        related_name="service_templates_using",
        verbose_name="software aplicable",
        help_text="Software que aplica a este servicio. El costo/hora se autocalcula de la suma.",
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
    def effective_hourly_rate(self) -> Decimal:
        """Tarifa horaria efectiva: usa hourly_rate si está, si no la del rol responsable."""
        if self.hourly_rate and self.hourly_rate > 0:
            return self.hourly_rate
        if self.responsible_role_id and self.responsible_role.default_hourly_rate:
            return self.responsible_role.default_hourly_rate
        return Decimal("0")

    @property
    def subtotal_honorarios(self) -> Decimal:
        return (self.effective_hourly_rate * self.estimated_hours).quantize(self._Q)

    # cached_property + iterar `.all()` (no `.filter()`): así el prefetch
    # cache de `hardwares` se respeta cuando el caller hace prefetch_related;
    # sin cache, list/export caían en N+1 contra hardwares × softwares.
    @cached_property
    def effective_hardware_cost_per_hour(self) -> Decimal:
        """Suma de depreciación/hora del hardware seleccionado; si no hay
        selección, cae al valor manual de hardware_cost_per_hour."""
        if self.pk:
            selected = [h for h in self.hardwares.all() if h.is_active]
            if selected:
                return sum(
                    (h.depreciation_per_hour or Decimal("0") for h in selected),
                    Decimal("0"),
                )
        return self.hardware_cost_per_hour or Decimal("0")

    @cached_property
    def effective_software_cost_per_hour(self) -> Decimal:
        """Suma de costo/hora del software seleccionado; si no hay selección,
        cae al valor manual de software_cost_per_hour."""
        if self.pk:
            selected = [s for s in self.softwares.all() if s.is_active]
            if selected:
                return sum(
                    (s.hourly_value or Decimal("0") for s in selected),
                    Decimal("0"),
                )
        return self.software_cost_per_hour or Decimal("0")

    @property
    def hardware_total(self) -> Decimal:
        return (self.effective_hardware_cost_per_hour * self.estimated_hours).quantize(self._Q)

    @property
    def software_total(self) -> Decimal:
        return (self.effective_software_cost_per_hour * self.estimated_hours).quantize(self._Q)

    @property
    def consumables_total(self) -> Decimal:
        return (self.consumables_per_hour * self.estimated_hours).quantize(self._Q)

    @property
    def costo_directo(self) -> Decimal:
        return (self.subtotal_honorarios + self.hardware_total + self.software_total + self.consumables_total + self.subcontracts).quantize(self._Q)

    # cached_property: get_current_prorrateo_rate hace 3 queries por llamada;
    # la cascada la invoca via prorrateo_gastos varias veces por fila. Caller
    # batch (excel_io.export_services) pre-puebla `__dict__` para evitar las
    # queries cross-instance cuando la línea operativa se repite.
    @cached_property
    def effective_prorrateo_rate(self) -> Decimal:
        """Tarifa de prorrateo desde el motor real; fallback a constante si no hay datos."""
        from domain.financials.cost_allocation import get_current_prorrateo_rate
        line_code = self.operative_line.code if self.operative_line_id else None
        return get_current_prorrateo_rate(line_code)

    @property
    def prorrateo_gastos(self) -> Decimal:
        return (self.effective_prorrateo_rate * self.estimated_hours).quantize(self._Q)

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
    Acción individual dentro de una actividad clave de servicio.
    Corresponde a la columna ACCIONES CLAVES del Excel D.sign DATA.
    """

    service_template = models.ForeignKey(
        ServiceTemplate,
        on_delete=models.CASCADE,
        related_name="activities",
        verbose_name="plantilla de servicio",
    )
    key_activity = models.ForeignKey(
        "KeyActivity",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="actions",
        verbose_name="actividad clave",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="orden",
    )
    name = models.TextField(
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
    name = models.TextField(
        verbose_name="nombre del entregable",
    )
    unit = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="unidad",
        help_text="Ej. Proyecto, 100m2, Und, 15 ha.",
    )
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=1,
        verbose_name="cantidad",
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
    name = models.TextField(
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
