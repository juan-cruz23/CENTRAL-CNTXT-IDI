from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from apps.common.models import TimeStampedModel


class WeeklyTimeDistribution(TimeStampedModel):
    """
    Weekly time distribution entry.
    Each user submits one record per week indicating the % of time
    spent on each active project.
    """

    class Status(models.TextChoices):
        DRAFT = "DRAFT", "Borrador"
        SUBMITTED = "SUBMITTED", "Enviado"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="time_distributions",
        verbose_name="usuario",
    )
    week_start = models.DateField(
        verbose_name="inicio de semana",
        help_text="Lunes de la semana reportada.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="estado",
    )
    submitted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="fecha de envío",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        unique_together = ("user", "week_start")
        ordering = ["-week_start"]
        verbose_name = "distribución semanal"
        verbose_name_plural = "distribuciones semanales"

    def __str__(self):
        return f"{self.user} - Semana {self.week_start}"

    @property
    def total_percentage(self):
        return sum(e.percentage for e in self.entries.all())

    @property
    def is_valid(self):
        return self.total_percentage == 100


class TimeDistributionEntry(TimeStampedModel):
    """
    Individual project entry within a weekly distribution.
    """

    distribution = models.ForeignKey(
        WeeklyTimeDistribution,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name="distribución",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="time_entries",
        verbose_name="proyecto",
    )
    percentage = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name="porcentaje",
    )

    class Meta:
        unique_together = ("distribution", "project")
        ordering = ["-percentage"]
        verbose_name = "entrada de distribución"
        verbose_name_plural = "entradas de distribución"

    def __str__(self):
        return f"{self.project.code} - {self.percentage}%"
