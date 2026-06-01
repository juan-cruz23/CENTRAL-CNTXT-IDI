from django.contrib.auth.models import AbstractUser
from django.db import models


class AccessPackage(models.Model):
    """Paquetes de acceso disponibles en la plataforma."""

    code = models.CharField(max_length=30, unique=True, verbose_name="código", help_text='Ej. "ESSENTIAL", "PREMIUM".')
    name = models.CharField(max_length=100, verbose_name="nombre")
    description = models.TextField(blank=True, verbose_name="descripción / qué incluye")
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        ordering = ["code"]
        verbose_name = "paquete de acceso"
        verbose_name_plural = "paquetes de acceso"

    def __str__(self):
        return self.name

    @property
    def project_count(self):
        return self.projects.count()


class User(AbstractUser):
    """Custom user model for Central Contexto 2.0."""

    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="teléfono",
    )
    avatar = models.ImageField(
        upload_to="avatars/",
        blank=True,
        null=True,
        verbose_name="avatar",
    )
    is_active_contractor = models.BooleanField(
        default=False,
        verbose_name="contratista activo",
    )
    hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="tarifa por hora",
    )
    hourly_overhead = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="sobrecosto por hora",
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return self.get_full_name() or self.username


class Role(models.Model):
    """Roles that can be assigned to users."""

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="código",
        help_text='Ej. "LP", "LA", "DO".',
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripción / permisos",
        help_text="Describe qué puede hacer este rol en la plataforma.",
    )
    default_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="tarifa por hora por defecto",
    )

    # Permission flags
    is_leader = models.BooleanField(
        default=False,
        verbose_name="puede liderar proyectos",
        help_text="Aparece en el selector de líder al crear/editar proyectos.",
    )
    can_access_financials = models.BooleanField(
        default=False,
        verbose_name="acceso a datos financieros",
        help_text="Puede ver valores, tarifas y rentabilidad.",
    )
    can_access_all_projects = models.BooleanField(
        default=False,
        verbose_name="ve todos los proyectos",
        help_text="Si está activo, ve todos los proyectos. Si no, solo los asignados.",
    )
    can_create_projects = models.BooleanField(
        default=False,
        verbose_name="puede crear proyectos",
        help_text="Puede crear nuevos proyectos en el sistema.",
    )
    can_edit_projects = models.BooleanField(
        default=False,
        verbose_name="puede editar proyectos",
        help_text="Puede editar y eliminar proyectos existentes.",
    )
    can_manage_third_parties = models.BooleanField(
        default=False,
        verbose_name="puede gestionar terceros",
        help_text="Puede crear y editar clientes, proveedores y terceros.",
    )
    can_manage_allocations = models.BooleanField(
        default=False,
        verbose_name="puede gestionar capacidad",
        help_text="Puede asignar y modificar la distribución de capacidad del equipo.",
    )

    # Visibility flags — controlan qué secciones del sidebar son visibles
    can_view_terceros = models.BooleanField(
        default=False,
        verbose_name="ve sección Terceros",
        help_text="Puede acceder al módulo de clientes y terceros.",
    )
    can_view_services = models.BooleanField(
        default=False,
        verbose_name="ve sección Servicios",
        help_text="Puede acceder al catálogo de servicios.",
    )
    can_view_pricing = models.BooleanField(
        default=False,
        verbose_name="ve sección Pricing",
        help_text="Puede acceder al dashboard de tarifas y precios.",
    )
    can_view_organization = models.BooleanField(
        default=False,
        verbose_name="ve sección Organización",
        help_text="Puede acceder a la configuración organizacional.",
    )
    can_view_portfolio = models.BooleanField(
        default=False,
        verbose_name="ve sección Portfolio",
        help_text="Puede acceder a la vista general de proyectos (Portfolio).",
    )
    can_view_capacity = models.BooleanField(
        default=False,
        verbose_name="ve sección Capacidad / Heatmap",
        help_text="Puede acceder a los módulos de capacidad y heatmap del equipo.",
    )
    can_view_timetracking = models.BooleanField(
        default=False,
        verbose_name="ve sección Mi Tiempo",
        help_text="Puede acceder al registro y reporte de tiempo.",
    )
    can_view_calendar = models.BooleanField(
        default=False,
        verbose_name="ve sección Calendario",
        help_text="Puede acceder a la sincronización y vista de calendario.",
    )
    can_import_data = models.BooleanField(
        default=False,
        verbose_name="puede importar datos",
        help_text="Puede usar el asistente de importación masiva de datos.",
    )
    can_manage_teams = models.BooleanField(
        default=False,
        verbose_name="puede gestionar equipos semanales",
        help_text="Puede crear y editar equipos de trabajo semanales por proyecto.",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        ordering = ["code"]
        verbose_name = "rol"
        verbose_name_plural = "roles"

    def __str__(self):
        return f"{self.code} - {self.name}"


class Badge(models.Model):
    """Medallas personalizadas que el admin otorga a los usuarios."""

    name = models.CharField(max_length=120, verbose_name="nombre", help_text='Ej. "Experta en parcelaciones"')
    emoji = models.CharField(max_length=10, default="🏅", verbose_name="emoji")
    color = models.CharField(max_length=7, default="#C8A87A", verbose_name="color (hex)", help_text="Color de acento, ej. #C8A87A")
    description = models.TextField(blank=True, verbose_name="descripción")
    is_active = models.BooleanField(default=True, verbose_name="activa")

    class Meta:
        ordering = ["name"]
        verbose_name = "medalla"
        verbose_name_plural = "medallas"

    def __str__(self):
        return f"{self.emoji} {self.name}"


class UserBadge(models.Model):
    """Asignación de una medalla a un usuario, otorgada por el admin."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="user_badges", verbose_name="usuario"
    )
    badge = models.ForeignKey(
        Badge, on_delete=models.CASCADE, related_name="user_badges", verbose_name="medalla"
    )
    granted_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="badges_granted", verbose_name="otorgada por",
    )
    granted_at = models.DateTimeField(auto_now_add=True, verbose_name="otorgada el")
    note = models.TextField(blank=True, verbose_name="nota / motivo")

    class Meta:
        unique_together = ("user", "badge")
        ordering = ["granted_at"]
        verbose_name = "medalla de usuario"
        verbose_name_plural = "medallas de usuarios"

    def __str__(self):
        return f"{self.user} — {self.badge}"


class WorkSchedule(models.Model):
    """Jornadas laborales estándar (horas por semana)."""

    name = models.CharField(max_length=100, verbose_name="nombre", help_text='Ej. "Tiempo completo", "Medio tiempo".')
    weekly_hours = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name="horas por semana",
    )
    is_active = models.BooleanField(default=True, verbose_name="activa")

    class Meta:
        ordering = ["-weekly_hours"]
        verbose_name = "jornada laboral"
        verbose_name_plural = "jornadas laborales"

    def __str__(self):
        return f"{self.name} ({self.weekly_hours}h/sem)"


class UserRole(models.Model):
    """Association between users and roles."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="usuario",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name="rol",
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="es principal",
    )

    class Meta:
        unique_together = ("user", "role")
        verbose_name = "rol de usuario"
        verbose_name_plural = "roles de usuario"

    def __str__(self):
        return f"{self.user} - {self.role}"
