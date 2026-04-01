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
