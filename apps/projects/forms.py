from decimal import Decimal, InvalidOperation

from django import forms

from apps.common.utils import format_cop, parse_cop_currency
from apps.projects.models import Client, Project, ServiceInstance


# ---------------------------------------------------------------------------
# Helpers for COP-formatted fields
# ---------------------------------------------------------------------------
class COPDecimalField(forms.DecimalField):
    """
    A DecimalField that accepts Colombian peso formatted input
    (e.g. "$40.000.000" or "1.200.000,50") and displays values
    in COP format.
    """

    def prepare_value(self, value):
        """Display value in COP format for the form widget."""
        if value is None:
            return ""
        if isinstance(value, str):
            return value
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, TypeError):
            return str(value)
        return format_cop(decimal_value)

    def clean(self, value):
        """Parse COP-formatted input to a Decimal."""
        if not value:
            return super().clean(value)
        if isinstance(value, str) and ("$" in value or "." in value or "," in value):
            parsed = parse_cop_currency(value)
            return super().clean(str(parsed))
        return super().clean(value)


# ---------------------------------------------------------------------------
# Project form
# ---------------------------------------------------------------------------
class ProjectForm(forms.ModelForm):
    """Form for creating and editing projects."""

    total_value = COPDecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Valor total",
    )

    class Meta:
        model = Project
        fields = [
            "code",
            "name",
            "client",
            "category",
            "client_category",
            "access_type",
            "location",
            "country",
            "status",
            "business_unit",
            "operative_line",
            "leader",
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
            "total_value",
            "iva_rate",
            "notes",
        ]
        widgets = {
            "planned_start_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "planned_end_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "actual_start_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "actual_end_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make date fields accept the HTML5 date format
        for field_name in (
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
        ):
            self.fields[field_name].input_formats = ["%Y-%m-%d"]


# ---------------------------------------------------------------------------
# Client form
# ---------------------------------------------------------------------------
class ClientForm(forms.ModelForm):
    """Form for creating and editing clients."""

    class Meta:
        model = Client
        fields = [
            "name",
            "company",
            "category",
            "email",
            "phone",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


# ---------------------------------------------------------------------------
# ServiceInstance form
# ---------------------------------------------------------------------------
class ServiceInstanceForm(forms.ModelForm):
    """
    Form for editing service instances.
    Financial fields accept COP-formatted input.
    """

    unit_price = COPDecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Precio unitario",
    )
    deductions = COPDecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Deducciones",
    )
    real_operative_cost = COPDecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Costo operativo real",
    )
    estimated_operative_cost = COPDecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Costo operativo estimado",
    )

    class Meta:
        model = ServiceInstance
        fields = [
            "code",
            "name",
            "quantity",
            "unit_price",
            "incidence_pct",
            "deductions",
            "real_operative_cost",
            "estimated_operative_cost",
            "margin_pct",
            "is_checked",
            "progress_pct",
            "is_real_checked",
            "expected_progress_pct",
            "responsible_role",
            "assigned_professional",
            "support_notes",
            "projected_hours",
            "projected_start_date",
            "actual_start_date",
            "projected_days",
            "projected_end_date",
            "actual_end_date",
            "actual_hours",
            "operative_deviation_pct",
            "is_milestone",
            "is_review_period",
        ]
        widgets = {
            "projected_start_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "actual_start_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "projected_end_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "actual_end_date": forms.DateInput(
                attrs={"type": "date"},
                format="%Y-%m-%d",
            ),
            "support_notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in (
            "projected_start_date",
            "actual_start_date",
            "projected_end_date",
            "actual_end_date",
        ):
            self.fields[field_name].input_formats = ["%Y-%m-%d"]
