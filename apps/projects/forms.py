from decimal import Decimal, InvalidOperation

from django import forms
from django.db.models import Case, Value, When

from apps.common.forms import DaisyUIFormMixin
from apps.common.utils import format_cop, parse_cop_currency
from apps.geography.models import Country, Municipality
from apps.projects.models import Client, Milestone, Project, ProjectPrerequisite, ProjectScope, ServiceInstance


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
class ProjectForm(DaisyUIFormMixin, forms.ModelForm):
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
            "municipality",
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
        for field_name in (
            "planned_start_date",
            "planned_end_date",
            "actual_start_date",
            "actual_end_date",
        ):
            self.fields[field_name].input_formats = ["%Y-%m-%d"]
        # En creación: ocultar código (se genera automáticamente)
        # En edición: mostrar como solo lectura
        for fname in ("leader", "client"):
            if fname in self.fields:
                cls = self.fields[fname].widget.attrs.get("class", "")
                self.fields[fname].widget.attrs["class"] = (cls + " js-select2").strip()

        if not self.instance.pk:
            self.fields.pop("code")
        else:
            self.fields["code"].widget.attrs["readonly"] = True
            self.fields["code"].widget.attrs["class"] = (
                self.fields["code"].widget.attrs.get("class", "") + " opacity-60 cursor-not-allowed"
            )


# ---------------------------------------------------------------------------
# Scope form
# ---------------------------------------------------------------------------
class ScopeForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectScope
        fields = ["name", "value", "status", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 2})}


# ---------------------------------------------------------------------------
# Prerequisite form
# ---------------------------------------------------------------------------
class PrerequisiteForm(DaisyUIFormMixin, forms.ModelForm):
    """Inline form for adding a prerequisite."""

    class Meta:
        model = ProjectPrerequisite
        fields = ["category", "prerequisite_type", "name", "weight_pct"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["prerequisite_type"].widget.attrs["placeholder"] = "Ej. Planos, Contrato..."
        self.fields["name"].widget.attrs["placeholder"] = "Descripción breve"


# ---------------------------------------------------------------------------
# Client form
# ---------------------------------------------------------------------------
class ClientForm(DaisyUIFormMixin, forms.ModelForm):
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
class ServiceInstanceForm(DaisyUIFormMixin, forms.ModelForm):
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
        self.project = kwargs.pop("project", None)
        super().__init__(*args, **kwargs)
        for field_name in (
            "projected_start_date",
            "actual_start_date",
            "projected_end_date",
            "actual_end_date",
        ):
            self.fields[field_name].input_formats = ["%Y-%m-%d"]

        # Smart ordering: professionals allocated to this project first
        if self.project and "assigned_professional" in self.fields:
            from apps.capacity.models import ProjectAllocation

            allocated_user_ids = ProjectAllocation.objects.filter(
                project=self.project,
            ).values_list("user_id", flat=True).distinct()

            from apps.accounts.models import User

            self.fields["assigned_professional"].queryset = (
                User.objects.filter(is_active=True)
                .annotate(
                    is_allocated=Case(
                        When(pk__in=allocated_user_ids, then=Value(0)),
                        default=Value(1),
                    )
                )
                .order_by("is_allocated", "first_name", "last_name")
            )

            # HTMX validation: check allocation when professional changes
            self.fields["assigned_professional"].widget.attrs.update({
                "hx-get": f"/proyectos/{self.project.pk}/validar-asignacion/",
                "hx-target": "#assignment-warning",
                "hx-trigger": "change",
                "hx-include": "[name='assigned_professional']",
            })


# ---------------------------------------------------------------------------
# Milestone form
# ---------------------------------------------------------------------------
class MilestoneForm(DaisyUIFormMixin, forms.ModelForm):
    """Inline form for adding a milestone."""

    class Meta:
        model = Milestone
        fields = ["milestone_type", "code", "name", "planned_date", "actual_date", "notes"]
        widgets = {
            "planned_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "actual_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ("planned_date", "actual_date"):
            self.fields[field_name].input_formats = ["%Y-%m-%d"]


# ---------------------------------------------------------------------------
# ServiceInstance create form (reduced fields)
# ---------------------------------------------------------------------------
class ServiceInstanceCreateForm(DaisyUIFormMixin, forms.ModelForm):
    """Simplified form for creating a new service instance."""

    unit_price = COPDecimalField(
        max_digits=14,
        decimal_places=2,
        required=False,
        label="Precio unitario",
    )

    class Meta:
        model = ServiceInstance
        fields = [
            "service_template",
            "code",
            "name",
            "quantity",
            "unit_price",
            "assigned_professional",
            "projected_start_date",
            "projected_end_date",
        ]
        widgets = {
            "projected_start_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "projected_end_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop("project", None)
        self.phase_instance = kwargs.pop("phase_instance", None)
        super().__init__(*args, **kwargs)
        for field_name in ("projected_start_date", "projected_end_date"):
            self.fields[field_name].input_formats = ["%Y-%m-%d"]
