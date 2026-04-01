from django.db import models

from apps.common.models import TimeStampedModel


class Country(TimeStampedModel):
    name = models.CharField(max_length=100, unique=True, verbose_name="nombre")
    iso_code = models.CharField(max_length=3, unique=True, verbose_name="código ISO")
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        verbose_name = "país"
        verbose_name_plural = "países"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Municipality(TimeStampedModel):
    name = models.CharField(max_length=150, verbose_name="nombre")
    department = models.CharField(max_length=100, verbose_name="departamento")
    country = models.ForeignKey(
        Country,
        on_delete=models.CASCADE,
        related_name="municipalities",
        verbose_name="país",
    )
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        verbose_name = "municipio"
        verbose_name_plural = "municipios"
        ordering = ["department", "name"]
        unique_together = [("name", "department", "country")]

    def __str__(self):
        return f"{self.department} — {self.name}"
