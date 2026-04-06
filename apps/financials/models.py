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


# ---------------------------------------------------------------------------
# Accounting (Loggro integration)
# ---------------------------------------------------------------------------
class AccountingAccount(TimeStampedModel):
    """Plan Unico de Cuentas importado de Loggro."""

    class AccountType(models.TextChoices):
        ASSET = "ASSET", "Activo"
        LIABILITY = "LIABILITY", "Pasivo"
        EQUITY = "EQUITY", "Patrimonio"
        REVENUE = "REVENUE", "Ingreso"
        EXPENSE = "EXPENSE", "Gasto"
        COST = "COST", "Costo"

    account_code = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="código de cuenta",
    )
    name = models.CharField(
        max_length=300,
        verbose_name="nombre",
    )
    account_type = models.CharField(
        max_length=20,
        choices=AccountType.choices,
        blank=True,
        verbose_name="tipo de cuenta",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activa",
    )

    class Meta:
        ordering = ["account_code"]
        verbose_name = "cuenta contable"
        verbose_name_plural = "cuentas contables"

    def __str__(self):
        return f"{self.account_code} - {self.name}"


class CostCenterMapping(TimeStampedModel):
    """Mapea centros de costo de Loggro a proyectos/unidades de negocio."""

    cost_center_code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="código centro de costo",
    )
    cost_center_name = models.CharField(
        max_length=200,
        verbose_name="nombre centro de costo",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="cost_center_mappings",
        verbose_name="proyecto",
    )
    business_unit = models.ForeignKey(
        "organizations.BusinessUnit",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name="unidad de negocio",
    )

    class Meta:
        ordering = ["cost_center_code"]
        verbose_name = "mapeo de centro de costo"
        verbose_name_plural = "mapeos de centros de costo"

    def __str__(self):
        return f"{self.cost_center_code} - {self.cost_center_name}"


class AccountingTransaction(TimeStampedModel):
    """Transacción contable individual importada de Loggro."""

    import_job = models.ForeignKey(
        "imports.ImportJob",
        on_delete=models.CASCADE,
        related_name="accounting_txns",
        verbose_name="trabajo de importación",
    )
    document_date = models.DateField(
        verbose_name="fecha documento",
    )
    document_type = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="tipo documento",
    )
    document_number = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="número documento",
    )
    account = models.ForeignKey(
        AccountingAccount,
        on_delete=models.CASCADE,
        related_name="transactions",
        verbose_name="cuenta",
    )
    cost_center = models.ForeignKey(
        CostCenterMapping,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="transactions",
        verbose_name="centro de costo",
    )
    third_party_nit = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="NIT tercero",
    )
    third_party_name = models.CharField(
        max_length=300,
        blank=True,
        verbose_name="nombre tercero",
    )
    description = models.TextField(
        blank=True,
        verbose_name="descripción",
    )
    debit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="débito",
    )
    credit = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="crédito",
    )
    balance = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="saldo",
    )
    period = models.CharField(
        max_length=7,
        verbose_name="periodo",
        help_text='Formato "YYYY-MM".',
    )

    class Meta:
        ordering = ["document_date", "pk"]
        indexes = [
            models.Index(fields=["period"], name="idx_acctxn_period"),
            models.Index(fields=["account", "period"], name="idx_acctxn_acc_period"),
        ]
        verbose_name = "transacción contable"
        verbose_name_plural = "transacciones contables"

    def __str__(self):
        return f"{self.document_date} - {self.account.account_code} - {self.description[:50]}"


# ---------------------------------------------------------------------------
# Cost Allocation (Prorrateo)
# ---------------------------------------------------------------------------
class CostAllocationPeriod(TimeStampedModel):
    """Periodo mensual de asignación de costos."""

    period = models.CharField(
        max_length=7,
        unique=True,
        verbose_name="periodo",
        help_text='Formato "YYYY-MM".',
    )
    start_date = models.DateField(
        verbose_name="fecha inicio",
    )
    end_date = models.DateField(
        verbose_name="fecha fin",
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name="cerrado",
    )
    total_costs = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="costos totales",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["-period"]
        verbose_name = "periodo de asignación"
        verbose_name_plural = "periodos de asignación"

    def __str__(self):
        return self.period


class CostAllocation(TimeStampedModel):
    """Asignación individual de costos a un proyecto para un periodo."""

    class CostType(models.TextChoices):
        OPERATIVE = "OPERATIVE", "Tiempo Operativo"
        STRATEGIC = "STRATEGIC", "Tiempo Estratégico"
        DIRECT = "DIRECT", "Costo Directo"

    period = models.ForeignKey(
        CostAllocationPeriod,
        on_delete=models.CASCADE,
        related_name="allocations",
        verbose_name="periodo",
    )
    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="cost_allocations",
        verbose_name="proyecto",
    )
    cost_type = models.CharField(
        max_length=20,
        choices=CostType.choices,
        verbose_name="tipo de costo",
    )
    allocated_amount = models.DecimalField(
        max_digits=14,
        decimal_places=2,
        default=0,
        verbose_name="monto asignado",
    )
    allocation_pct = models.DecimalField(
        max_digits=7,
        decimal_places=4,
        default=0,
        verbose_name="% asignación",
    )
    source_description = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="descripción de origen",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        ordering = ["period", "project"]
        verbose_name = "asignación de costos"
        verbose_name_plural = "asignaciones de costos"

    def __str__(self):
        return f"{self.period} - {self.project} - {self.get_cost_type_display()}"


class OperationalExpenseType(TimeStampedModel):
    """Tipos de gasto operacional. Los valores se registran por período, no aquí."""

    name = models.CharField(max_length=200, verbose_name="nombre")
    is_active = models.BooleanField(default=True, verbose_name="activo")

    class Meta:
        ordering = ["name"]
        verbose_name = "tipo de gasto operacional"
        verbose_name_plural = "tipos de gasto operacional"

    def __str__(self):
        return self.name


class ColombianHoliday(TimeStampedModel):
    """Festivos colombianos para calculos de dias habiles."""

    class HolidayType(models.TextChoices):
        NATIONAL = "NATIONAL", "Nacional"
        COMPANY = "COMPANY", "CNTXT"

    date = models.DateField(
        unique=True,
        verbose_name="fecha",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )
    holiday_type = models.CharField(
        max_length=10,
        choices=HolidayType.choices,
        default=HolidayType.NATIONAL,
        verbose_name="tipo",
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
