from datetime import date
from decimal import Decimal

from django.db import models

from apps.common.models import TimeStampedModel


# ---------------------------------------------------------------------------
# Client
# ---------------------------------------------------------------------------
class Client(TimeStampedModel):
    """Client entity managed by Contexto."""

    class Category(models.TextChoices):
        BLACK = "BLACK", "Black"
        GOLD = "GOLD", "Gold"
        SILVER = "SILVER", "Silver"
        SELECT = "SELECT", "Select"

    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="empresa",
    )
    category = models.CharField(
        max_length=10,
        choices=Category.choices,
        verbose_name="categoría",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="correo electrónico",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="teléfono",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------
class Project(TimeStampedModel):
    """
    Core project model - the heart of Central Contexto 2.0.
    Each project is identified by a numeric code (e.g. '216') and tracks
    financial, scheduling and quality metrics.
    """

    class ClientCategory(models.TextChoices):
        BLACK = "BLACK", "Black"
        GOLD = "GOLD", "Gold"
        SILVER = "SILVER", "Silver"
        SELECT = "SELECT", "Select"

    class AccessType(models.TextChoices):
        PREMIUM = "PREMIUM", "PREMIUM ACCESS"
        STANDARD = "STANDARD", "STANDARD ACCESS"

    # kept for data-migration compatibility only

    class Status(models.TextChoices):
        PLANNING = "PLANNING", "Planeación"
        ACTIVE = "ACTIVE", "Activo"
        PAUSED = "PAUSED", "Pausado"
        COMPLETED = "COMPLETED", "Completado"
        CANCELLED = "CANCELLED", "Cancelado"

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="código",
        help_text='Código único del proyecto, ej. "216".',
    )
    name = models.CharField(
        max_length=300,
        verbose_name="nombre",
        help_text='Nombre del proyecto, ej. "Casa Saint Regis".',
    )
    client = models.ForeignKey(
        Client,
        on_delete=models.CASCADE,
        related_name="projects",
        verbose_name="cliente",
    )
    third_party = models.ForeignKey(
        "terceros.ThirdParty",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="tercero",
    )
    category = models.ForeignKey(
        "services.ProjectCategory",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="categoría de proyecto",
    )
    client_category = models.CharField(
        max_length=10,
        blank=True,
        choices=ClientCategory.choices,
        verbose_name="categoría de cliente",
    )
    access_type = models.CharField(
        max_length=20,
        choices=AccessType.choices,
        default=AccessType.STANDARD,
        verbose_name="tipo de acceso (legado)",
    )
    access_package = models.ForeignKey(
        "accounts.AccessPackage",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="paquete de acceso",
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="ciudad / municipio (texto libre)",
    )
    country = models.CharField(
        max_length=100,
        default="Colombia",
        verbose_name="país",
    )
    municipality = models.ForeignKey(
        "geography.Municipality",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="projects",
        verbose_name="municipio",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING,
        verbose_name="estado",
    )
    business_unit = models.ForeignKey(
        "organizations.BusinessUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="unidad de negocio",
    )
    operative_line = models.ForeignKey(
        "organizations.OperativeLine",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="línea operativa",
    )
    leader = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_projects",
        verbose_name="líder",
    )

    # Scheduling
    planned_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha planeada de inicio",
    )
    planned_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha planeada de fin",
    )
    actual_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real de inicio",
    )
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real de fin",
    )

    # Financial
    total_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor total",
    )
    iva_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=19,
        verbose_name="tasa de IVA",
    )

    # Metrics
    current_progress_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="porcentaje de avance actual",
    )
    schedule_deviation_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="desviación de cronograma (%)",
    )
    profitability_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="rentabilidad (%)",
    )
    client_satisfaction_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="puntaje de satisfacción del cliente",
    )

    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "proyecto"
        verbose_name_plural = "proyectos"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def planned_duration_days(self):
        """Return the number of days between planned start and end dates, or None."""
        if self.planned_start_date and self.planned_end_date:
            return (self.planned_end_date - self.planned_start_date).days
        return None

    @property
    def is_overdue(self):
        """Return True if the project is past its planned end date and not completed/cancelled."""
        if (
            self.planned_end_date
            and self.status not in (self.Status.COMPLETED, self.Status.CANCELLED)
            and date.today() > self.planned_end_date
        ):
            return True
        return False


# ---------------------------------------------------------------------------
# ProjectScope
# ---------------------------------------------------------------------------
class ProjectScope(TimeStampedModel):
    """Alcance contractual pactado con el cliente."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        IN_PROGRESS = "IN_PROGRESS", "En ejecución"
        DELIVERED = "DELIVERED", "Entregado"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="scopes",
        verbose_name="proyecto",
    )
    name = models.CharField(max_length=300, verbose_name="nombre")
    description = models.TextField(blank=True, verbose_name="descripción")
    value = models.DecimalField(
        max_digits=14, decimal_places=2, null=True, blank=True, verbose_name="valor"
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="estado",
    )
    notes = models.TextField(blank=True, verbose_name="notas")

    class Meta:
        ordering = ["created_at"]
        verbose_name = "alcance contractual"
        verbose_name_plural = "alcances contractuales"

    def __str__(self):
        return self.name


# ---------------------------------------------------------------------------
# ProjectPrerequisite
# ---------------------------------------------------------------------------
class ProjectPrerequisite(TimeStampedModel):
    """
    Tracks prerequisites, risk management items, and communication
    requirements that must be completed before or during a project.
    """

    class Category(models.TextChoices):
        PREREQUISITO = "PREREQUISITO", "Prerequisito"
        GESTION_RIESGO = "GESTION_RIESGO", "Gestión de Riesgo"
        COMUNICACION = "COMUNICACION", "Comunicación"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="prerequisites",
        verbose_name="proyecto",
    )
    category = models.CharField(
        max_length=30,
        choices=Category.choices,
        verbose_name="categoría",
    )
    prerequisite_type = models.CharField(
        max_length=100,
        verbose_name="tipo de prerequisito",
        help_text='Ej. "Técnicos", "Conceptuales", "Ficha de Proyecto", "Canal de Slack".',
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )
    is_completed = models.BooleanField(
        default=False,
        verbose_name="completado",
    )
    document = models.ForeignKey(
        "documents.ProjectDocument",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="prerequisites",
        verbose_name="documento adjunto",
    )
    weight_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("8.33"),
        verbose_name="peso (%)",
    )

    class Meta:
        ordering = ["project", "category", "prerequisite_type"]
        unique_together = ("project", "category", "prerequisite_type")
        verbose_name = "prerequisito de proyecto"
        verbose_name_plural = "prerequisitos de proyecto"

    def __str__(self):
        return f"{self.project.code} - {self.category} - {self.name}"


# ---------------------------------------------------------------------------
# PrerequisiteTemplate
# ---------------------------------------------------------------------------
class PrerequisiteTemplate(TimeStampedModel):
    """
    Defines a set of standard prerequisites for a given project category.
    When a project is created (or when the user clicks 'Cargar plantilla'),
    these items are automatically created as ProjectPrerequisite instances.
    """

    project_category = models.ForeignKey(
        "services.ProjectCategory",
        on_delete=models.CASCADE,
        related_name="prerequisite_templates",
        verbose_name="categoría de proyecto",
    )
    category = models.CharField(
        max_length=30,
        choices=ProjectPrerequisite.Category.choices,
        verbose_name="categoría de prerequisito",
    )
    prerequisite_type = models.CharField(
        max_length=100,
        verbose_name="tipo de prerequisito",
        help_text='Ej. "Técnicos", "Ficha de Proyecto", "Canal de Slack".',
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="descripción / notas",
    )
    weight_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal("8.33"),
        verbose_name="peso (%)",
    )
    reference_link = models.URLField(
        blank=True,
        verbose_name="enlace de referencia",
        help_text="URL a un documento o recurso de referencia.",
    )
    reference_file = models.FileField(
        upload_to="prereq_templates/",
        blank=True,
        null=True,
        verbose_name="archivo adjunto",
    )

    class Meta:
        ordering = ["project_category", "category", "prerequisite_type"]
        verbose_name = "plantilla de prerequisito"
        verbose_name_plural = "plantillas de prerequisitos"

    def __str__(self):
        return f"{self.project_category} — {self.prerequisite_type}"


# ---------------------------------------------------------------------------
# ProjectPhaseInstance
# ---------------------------------------------------------------------------
class ProjectPhaseInstance(TimeStampedModel):
    """
    Represents a concrete instance of a service phase within a project.
    Links a Project to a ProjectPhase template.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="phase_instances",
        verbose_name="proyecto",
    )
    phase = models.ForeignKey(
        "services.ProjectPhase",
        on_delete=models.CASCADE,
        verbose_name="fase",
    )
    order = models.PositiveIntegerField(
        default=1,
        verbose_name="orden",
    )
    planned_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha planeada de inicio",
    )
    planned_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha planeada de fin",
    )
    actual_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real de inicio",
    )
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real de fin",
    )
    total_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor total",
    )
    progress_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="porcentaje de avance",
    )

    class Meta:
        ordering = ["project", "order"]
        unique_together = ("project", "phase")
        verbose_name = "instancia de fase"
        verbose_name_plural = "instancias de fases"

    def __str__(self):
        return f"{self.project.code} - Fase {self.order}"


# ---------------------------------------------------------------------------
# ServiceInstance
# ---------------------------------------------------------------------------
class ServiceInstance(TimeStampedModel):
    """
    The most important operational model: a concrete service line item within
    a project phase.  Tracks costs, progress, scheduling and assignments for
    every individual service that Contexto delivers.
    """

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="service_instances",
        verbose_name="proyecto",
    )
    phase_instance = models.ForeignKey(
        ProjectPhaseInstance,
        on_delete=models.CASCADE,
        related_name="service_instances",
        verbose_name="instancia de fase",
        null=True,
        blank=True,
    )
    service_template = models.ForeignKey(
        "services.ServiceTemplate",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="plantilla de servicio",
    )

    # Identification
    code = models.CharField(
        max_length=20,
        verbose_name="código",
    )
    name = models.CharField(
        max_length=500,
        verbose_name="nombre",
    )

    # Financial
    quantity = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=1,
        verbose_name="cantidad",
    )
    unit_price = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="precio unitario",
    )
    total_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor total",
    )
    incidence_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="incidencia (%)",
    )
    deductions = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="deducciones",
    )
    real_operative_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costo operativo real",
    )
    estimated_operative_cost = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costo operativo estimado",
    )
    margin_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="margen (%)",
    )

    # Progress tracking
    is_checked = models.BooleanField(
        default=False,
        verbose_name="servicio check",
        help_text="Servicio Check",
    )
    progress_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="porcentaje de avance",
        help_text="Porcentaje de avance",
    )
    is_real_checked = models.BooleanField(
        default=False,
        verbose_name="check real",
        help_text="Check Real",
    )
    expected_progress_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="porcentaje de avance esperado",
    )

    # Assignment
    responsible_role = models.ForeignKey(
        "accounts.Role",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="rol responsable",
    )
    assigned_professional = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_services",
        verbose_name="profesional asignado",
    )
    support_notes = models.TextField(
        blank=True,
        verbose_name="observaciones de apoyos",
        help_text="Observaciones de Apoyos",
    )

    # Scheduling
    projected_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="horas proyectadas",
    )
    projected_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha proyectada de inicio",
    )
    actual_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real de inicio",
    )
    projected_days = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="días proyectados",
    )
    projected_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha proyectada de fin",
    )
    actual_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real de fin",
    )
    actual_hours = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        default=0,
        verbose_name="horas reales",
    )
    operative_deviation_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="desfase operativo (%)",
        help_text="Desfase Operativo",
    )

    # Flags
    is_milestone = models.BooleanField(
        default=False,
        verbose_name="es hito",
    )
    is_review_period = models.BooleanField(
        default=False,
        verbose_name="es período de revisión",
    )

    class Meta:
        ordering = ["phase_instance", "code"]
        verbose_name = "instancia de servicio"
        verbose_name_plural = "instancias de servicios"

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_complete(self):
        """
        A service is considered complete when it is checked AND its progress
        percentage meets or exceeds its incidence within the phase.
        """
        return self.is_checked and self.progress_pct >= self.incidence_pct

    def save(self, *args, **kwargs):
        """Compute total_value as quantity * unit_price before saving."""
        self.total_value = self.quantity * self.unit_price
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# Milestone
# ---------------------------------------------------------------------------
class Milestone(TimeStampedModel):
    """
    Key milestone events within a project, such as kick-offs, phase
    deliveries, client reviews, and final deliveries.
    """

    class MilestoneType(models.TextChoices):
        KICKOFF = "KICKOFF", "Kick-off"
        PHASE_DELIVERY = "PHASE_DELIVERY", "Entrega de Fase"
        CLIENT_REVIEW = "CLIENT_REVIEW", "Revisión de Cliente"
        FINAL_DELIVERY = "FINAL_DELIVERY", "Entrega Final"

    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="milestones",
        verbose_name="proyecto",
    )
    phase_instance = models.ForeignKey(
        ProjectPhaseInstance,
        on_delete=models.CASCADE,
        related_name="milestones",
        null=True,
        blank=True,
        verbose_name="instancia de fase",
    )
    code = models.CharField(
        max_length=20,
        verbose_name="código",
        help_text='Ej. "HITO 1".',
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
        help_text='Ej. "ENTREGA FASE 1".',
    )
    milestone_type = models.CharField(
        max_length=20,
        choices=MilestoneType.choices,
        verbose_name="tipo de hito",
    )
    planned_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha planeada",
    )
    actual_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha real",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["project", "planned_date"]
        verbose_name = "hito"
        verbose_name_plural = "hitos"

    def __str__(self):
        return f"{self.code} - {self.name}"
