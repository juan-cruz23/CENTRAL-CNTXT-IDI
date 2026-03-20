from django.conf import settings
from django.db import models

from apps.common.models import TimeStampedModel


class GoogleCalendarConnection(TimeStampedModel):
    """Stores OAuth2 credentials for a user's Google Calendar."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_connection",
        verbose_name="usuario",
    )
    access_token = models.TextField(
        blank=True,
        verbose_name="token de acceso",
    )
    refresh_token = models.TextField(
        blank=True,
        verbose_name="token de refresco",
    )
    token_expiry = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="expiración del token",
    )
    calendar_id = models.CharField(
        max_length=200,
        default="primary",
        verbose_name="ID del calendario",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )
    last_sync = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="última sincronización",
    )

    class Meta:
        verbose_name = "conexión de Google Calendar"
        verbose_name_plural = "conexiones de Google Calendar"

    def __str__(self):
        return f"Calendar: {self.user}"


class CalendarEvent(TimeStampedModel):
    """
    An event imported from Google Calendar,
    associated with a project for time tracking.
    """

    class MatchMethod(models.TextChoices):
        AUTO_NAME = "AUTO_NAME", "Automático (nombre)"
        AUTO_COLOR = "AUTO_COLOR", "Automático (color)"
        MANUAL = "MANUAL", "Manual"
        UNMATCHED = "UNMATCHED", "Sin asignar"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="calendar_events",
        verbose_name="usuario",
    )
    google_event_id = models.CharField(
        max_length=255,
        verbose_name="ID del evento en Google",
    )
    title = models.CharField(
        max_length=500,
        verbose_name="título",
    )
    start_time = models.DateTimeField(
        verbose_name="inicio",
    )
    end_time = models.DateTimeField(
        verbose_name="fin",
    )
    duration_hours = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0,
        verbose_name="duración (horas)",
    )
    color_id = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="color del evento",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="calendar_events",
        verbose_name="proyecto",
    )
    match_method = models.CharField(
        max_length=20,
        choices=MatchMethod.choices,
        default=MatchMethod.UNMATCHED,
        verbose_name="método de asignación",
    )
    is_meeting = models.BooleanField(
        default=False,
        verbose_name="es reunión",
        help_text="True si el evento tiene otros asistentes.",
    )

    class Meta:
        unique_together = ("user", "google_event_id")
        ordering = ["-start_time"]
        verbose_name = "evento de calendario"
        verbose_name_plural = "eventos de calendario"

    def __str__(self):
        return f"{self.title} ({self.start_time.date()})"

    def save(self, *args, **kwargs):
        if self.start_time and self.end_time:
            delta = self.end_time - self.start_time
            self.duration_hours = round(delta.total_seconds() / 3600, 2)
        super().save(*args, **kwargs)


class ProjectColorMapping(TimeStampedModel):
    """Maps Google Calendar color IDs to projects."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="color_mappings",
        verbose_name="usuario",
    )
    color_id = models.CharField(
        max_length=20,
        verbose_name="ID de color en Google Calendar",
    )
    color_name = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="nombre del color",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="color_mappings",
        verbose_name="proyecto",
    )

    class Meta:
        unique_together = ("user", "color_id")
        verbose_name = "mapeo de color a proyecto"
        verbose_name_plural = "mapeos de color a proyecto"

    def __str__(self):
        return f"{self.color_name or self.color_id} → {self.project.code}"


class ProjectKeywordMapping(TimeStampedModel):
    """Maps keywords in event titles to projects."""

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="keyword_mappings",
        verbose_name="proyecto",
    )
    keyword = models.CharField(
        max_length=100,
        verbose_name="palabra clave",
        help_text="Si el título del evento contiene esta palabra, se asocia al proyecto.",
    )

    class Meta:
        ordering = ["project", "keyword"]
        verbose_name = "mapeo de palabra clave"
        verbose_name_plural = "mapeos de palabras clave"

    def __str__(self):
        return f"'{self.keyword}' → {self.project.code}"
