from django.db import models

from apps.common.models import TimeStampedModel


class PaymentMilestone(TimeStampedModel):
    """Hitos de pago asociados a un proyecto."""

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pendiente"
        INVOICED = "INVOICED", "Facturado"
        COLLECTED = "COLLECTED", "Recaudado"
        OVERDUE = "OVERDUE", "Vencido"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="payment_milestones",
        verbose_name="proyecto",
    )
    concept = models.CharField(
        max_length=200,
        verbose_name="concepto",
        help_text='Ej: "Anticipo", "Abono 2", "Pago Final"',
    )
    proposed_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor propuesto",
    )
    iva_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor IVA",
    )
    incidence_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="% incidencia",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="estado",
    )
    discount_pct = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="% descuento",
    )
    discount_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor descuento",
    )
    executed_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor ejecutado",
    )
    billing_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de facturación",
    )
    invoice_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="número de factura",
    )
    invoice_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor factura",
    )
    collection_value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor recaudo",
    )
    collection_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de recaudo",
    )
    difference = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="diferencia",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["project", "incidence_pct"]
        verbose_name = "hito de pago"
        verbose_name_plural = "hitos de pago"

    def __str__(self):
        return f"{self.project} - {self.concept}"

    @property
    def total_with_iva(self):
        """Retorna el valor propuesto mas el IVA."""
        return self.proposed_value + self.iva_value

    def save(self, *args, **kwargs):
        self.difference = self.executed_value - self.proposed_value
        super().save(*args, **kwargs)


class ProfitabilitySummary(TimeStampedModel):
    """Resumen de rentabilidad por hito de entrega de un proyecto."""

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="profitability_summaries",
        verbose_name="proyecto",
    )
    milestone_name = models.CharField(
        max_length=200,
        verbose_name="nombre del hito",
        help_text='Ej: "Entrega 1", "Entrega 2"',
    )
    value = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="valor",
    )
    months_invested = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="meses invertidos",
    )
    analysis_costs = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costos de analisis",
    )
    total_costs = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costos totales",
    )
    expenses = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="gastos",
    )
    cost_plus_expenses_monthly = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costo + gastos mensual",
    )
    cost_plus_expenses_total = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costo + gastos total",
    )
    revenue = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="ingresos",
    )
    utility = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="utilidad",
    )
    margin_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="% margen",
    )
    utility_monthly = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="utilidad mensual",
    )
    margin_monthly_pct = models.DecimalField(
        max_digits=7,
        decimal_places=2,
        default=0,
        verbose_name="% margen mensual",
    )
    is_verified = models.BooleanField(
        default=False,
        verbose_name="verificado",
    )

    class Meta:
        ordering = ["project", "milestone_name"]
        verbose_name = "resumen de rentabilidad"
        verbose_name_plural = "resumenes de rentabilidad"

    def __str__(self):
        return f"{self.project} - {self.milestone_name}"


class ColombianHoliday(TimeStampedModel):
    """Festivos colombianos para calculos de dias habiles."""

    date = models.DateField(
        unique=True,
        verbose_name="fecha",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )

    class Meta:
        ordering = ["date"]
        verbose_name = "festivo colombiano"
        verbose_name_plural = "festivos colombianos"

    def __str__(self):
        return f"{self.date} - {self.name}"

    @classmethod
    def is_holiday(cls, check_date):
        """Verifica si una fecha dada es un festivo colombiano."""
        return cls.objects.filter(date=check_date).exists()

    @classmethod
    def holidays_in_range(cls, start_date, end_date):
        """Retorna los festivos colombianos en un rango de fechas."""
        return cls.objects.filter(date__gte=start_date, date__lte=end_date)
