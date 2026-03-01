from django.contrib.auth.models import AbstractUser
from django.db import models


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

    class RoleCode(models.TextChoices):
        LA = "LA", "Líder de Área"
        INT = "INT", "Interventor"
        VS = "VS", "Visor de Seguimiento"
        VL = "VL", "Visor Libre"
        DM = "DM", "Director de Medios"
        AI_I = "AI_I", "AI Individual"
        AI_M = "AI_M", "AI Masivo"

    code = models.CharField(
        max_length=10,
        unique=True,
        choices=RoleCode.choices,
        verbose_name="código",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
    )
    default_hourly_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="tarifa por hora por defecto",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripción",
    )

    class Meta:
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
