from django.conf import settings
from django.db import models


class WeeklyTeam(models.Model):
    """Equipo de trabajo armado para un proyecto en una semana específica."""

    project_name = models.CharField(
        max_length=200,
        verbose_name="proyecto",
        help_text="Nombre del proyecto o contexto del equipo.",
    )
    week_number = models.PositiveSmallIntegerField(verbose_name="semana ISO")
    year = models.PositiveSmallIntegerField(verbose_name="año")
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="teams_created",
        verbose_name="creado por",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-year", "-week_number", "project_name"]
        verbose_name = "equipo semanal"
        verbose_name_plural = "equipos semanales"

    def __str__(self):
        return f"Sem {self.week_number}/{self.year} — {self.project_name}"

    @property
    def label(self):
        return f"Semana #{self.week_number}"


class WeeklyTeamMember(models.Model):
    """Profesional integrante de un equipo semanal."""

    team = models.ForeignKey(
        WeeklyTeam,
        on_delete=models.CASCADE,
        related_name="members",
        verbose_name="equipo",
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="weekly_team_memberships",
        verbose_name="profesional",
    )
    occupation = models.CharField(
        max_length=60,
        verbose_name="ocupación",
        help_text="Una palabra o frase corta que describe su foco esta semana.",
    )
    order = models.PositiveSmallIntegerField(default=0, verbose_name="orden")

    class Meta:
        ordering = ["order", "user__first_name"]
        verbose_name = "integrante de equipo"
        verbose_name_plural = "integrantes de equipo"

    def __str__(self):
        return f"{self.user.get_full_name()} — {self.occupation}"
