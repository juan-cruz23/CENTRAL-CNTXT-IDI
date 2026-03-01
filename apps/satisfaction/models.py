from django.db import models

from apps.common.models import TimeStampedModel


# ---------------------------------------------------------------------------
# SatisfactionMeasurement (CVE - Calidad de Valor Emocional)
# ---------------------------------------------------------------------------
class SatisfactionMeasurement(TimeStampedModel):
    """
    CVE (Calidad de Valor Emocional) measurement for a project.
    Captures observed emotion, spontaneous phrases, and symbolic objects
    to compute an overall CVE score.
    """

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="satisfaction_measurements",
        verbose_name="proyecto",
    )
    milestone = models.ForeignKey(
        "projects.Milestone",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="hito",
    )
    measurement_date = models.DateField(
        verbose_name="fecha de medición",
    )
    observed_emotion_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="emoción observada",
        help_text="Emoción Observada",
    )
    spontaneous_phrase_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="frase espontánea",
        help_text="Frase Espontánea",
    )
    audio_video_link = models.URLField(
        blank=True,
        verbose_name="audio | video",
        help_text="Audio | Video",
    )
    symbolic_object_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="objeto simbólico",
        help_text="Objeto Simbólico",
    )
    cve_score = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="puntuación CVE",
        help_text="Puntuación CVE",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["-measurement_date"]
        verbose_name = "medición de satisfacción"
        verbose_name_plural = "mediciones de satisfacción"

    def __str__(self):
        return f"{self.project} - CVE {self.cve_score} ({self.measurement_date})"

    def save(self, *args, **kwargs):
        """Compute CVE score as the average of the three dimension percentages."""
        self.cve_score = (
            self.observed_emotion_pct
            + self.spontaneous_phrase_pct
            + self.symbolic_object_pct
        ) / 3
        super().save(*args, **kwargs)


# ---------------------------------------------------------------------------
# SatisfactionSurvey (Encuesta de Asertividad)
# ---------------------------------------------------------------------------
class SatisfactionSurvey(TimeStampedModel):
    """
    Encuesta de Asertividad linked to a CVE measurement.
    Captures six subjective dimensions and computes a total score.
    """

    measurement = models.OneToOneField(
        SatisfactionMeasurement,
        on_delete=models.CASCADE,
        related_name="survey",
        verbose_name="medición",
    )
    general_sensation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="sensación general del proceso",
        help_text="Sensación general del proceso",
    )
    clarity_and_support = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="claridad y acompañamiento",
        help_text="Claridad y acompañamiento",
    )
    personal_effort = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="esfuerzo personal",
        help_text="Esfuerzo personal",
    )
    team_relationship = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="relación con el equipo",
        help_text="Relación con el equipo",
    )
    confidence = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="confianza",
        help_text="Confianza",
    )
    perceived_value = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="valor percibido",
        help_text="Valor percibido",
    )
    total_score_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="puntuación total (%)",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        verbose_name = "encuesta de asertividad"
        verbose_name_plural = "encuestas de asertividad"

    def __str__(self):
        return f"Encuesta - {self.measurement} ({self.total_score_pct}%)"

    def save(self, *args, **kwargs):
        """Compute total score as the average of all six dimension fields."""
        self.total_score_pct = (
            self.general_sensation
            + self.clarity_and_support
            + self.personal_effort
            + self.team_relationship
            + self.confidence
            + self.perceived_value
        ) / 6
        super().save(*args, **kwargs)
