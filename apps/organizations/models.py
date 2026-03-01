from django.db import models

from apps.common.models import TimeStampedModel


class OrganizationalSystem(TimeStampedModel):
    """
    Represents a high-level organizational system within Contexto.
    Each system has a metaphorical analogy name that reflects its function.
    """

    class SystemCode(models.TextChoices):
        NEO = "NEO", "NEO"
        IDI = "IDI", "IDI"
        RED = "RED", "RED"
        CASH = "CASH", "CASH"
        CORE = "CORE", "CORE"
        BONES = "BONES", "BONES"

    code = models.CharField(
        max_length=10,
        unique=True,
        choices=SystemCode.choices,
        verbose_name="c\u00f3digo",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
    )
    analogy = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="analog\u00eda",
        help_text="Nombre metaf\u00f3rico del sistema.",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripci\u00f3n",
    )
    leader = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_systems",
        verbose_name="l\u00edder",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        ordering = ["code"]
        verbose_name = "sistema organizacional"
        verbose_name_plural = "sistemas organizacionales"

    def __str__(self):
        return f"{self.code} - {self.name}"


class BusinessUnit(TimeStampedModel):
    """
    Represents a business unit such as MADE or SELECT.
    """

    class UnitCode(models.TextChoices):
        MADE = "MADE", "MADE"
        SELECT = "SELECT", "SELECT"

    code = models.CharField(
        max_length=10,
        unique=True,
        choices=UnitCode.choices,
        verbose_name="c\u00f3digo",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripci\u00f3n",
    )
    leader = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="led_units",
        verbose_name="l\u00edder",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )

    class Meta:
        verbose_name = "unidad de negocio"
        verbose_name_plural = "unidades de negocio"

    def __str__(self):
        return f"{self.code} - {self.name}"


class OperativeLine(TimeStampedModel):
    """
    Represents an operative line within a business unit.
    Examples: 'Dise\u00f1o y Visual', 'Visualizaci\u00f3n', 'Tech Ventas', 'Intel Financiera'.
    """

    code = models.CharField(
        max_length=20,
        unique=True,
        verbose_name="c\u00f3digo",
    )
    name = models.CharField(
        max_length=100,
        verbose_name="nombre",
        help_text="Ej. 'Dise\u00f1o y Visual', 'Visualizaci\u00f3n', 'Tech Ventas', 'Intel Financiera'.",
    )
    business_unit = models.ForeignKey(
        BusinessUnit,
        on_delete=models.CASCADE,
        related_name="operative_lines",
        verbose_name="unidad de negocio",
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
        verbose_name = "l\u00ednea operativa"
        verbose_name_plural = "l\u00edneas operativas"

    def __str__(self):
        return f"{self.code} - {self.name}"
