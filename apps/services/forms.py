from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.services.models import Deliverable, Hardware, ProjectCategory, ProjectPhase, ServiceActivity, ServiceSubCategory, ServiceTemplate, Software


class ProjectCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ["code", "name", "description", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class HardwareForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Hardware
        fields = ["name", "value", "depreciation_per_hour", "is_active"]
        widgets = {"name": forms.TextInput(attrs={"placeholder": "Ej. Workstation Alta Gama (opcional)"})}


class SoftwareForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Software
        fields = ["name", "annual_value", "hourly_value", "is_active"]


class ProjectPhaseForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = ["number", "name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ServiceSubCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceSubCategory
        fields = ["code", "name", "description", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ServiceTemplateForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceTemplate
        fields = [
            "code",
            "name",
            "category",
            "phase",
            "subcategory",
            "operative_line",
            "responsible_role",
            "base_unit_price",
            "estimated_hours",
            "estimated_days",
            "target_margin_pct",
            "hourly_rate",
            "hardware_cost_per_hour",
            "software_cost_per_hour",
            "consumables_per_hour",
            "subcontracts",
            "contingency_pct",
            "utility_pct",
            "negotiation_pct",
            "description",
            "is_active",
        ]
        _pricing_attrs = {"class": "form-control", "hx-post": "/servicios/calcular-pricing/",
                          "hx-trigger": "change", "hx-include": "closest form",
                          "hx-target": "#pricing-breakdown", "hx-swap": "innerHTML"}
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "phase": forms.Select(attrs={"class": "form-select"}),
            "subcategory": forms.Select(attrs={"class": "form-select"}),
            "operative_line": forms.Select(attrs={"class": "form-select"}),
            "responsible_role": forms.Select(attrs={"class": "form-select"}),
            "base_unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "estimated_hours": forms.NumberInput(attrs={
                "class": "form-control",
                "hx-post": "/servicios/calcular-horas-dias/",
                "hx-trigger": "change",
                "hx-include": "[name='estimated_hours']",
                "hx-target": "#id_estimated_days",
                "hx-swap": "outerHTML",
                "name": "estimated_hours",
            }),
            "estimated_days": forms.NumberInput(attrs={
                "class": "form-control",
                "hx-post": "/servicios/calcular-horas-dias/",
                "hx-trigger": "change",
                "hx-include": "[name='estimated_days']",
                "hx-target": "#id_estimated_hours",
                "hx-swap": "outerHTML",
                "name": "estimated_days",
            }),
            "target_margin_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "hourly_rate": forms.NumberInput(attrs={**_pricing_attrs}),
            "hardware_cost_per_hour": forms.NumberInput(attrs={**_pricing_attrs}),
            "software_cost_per_hour": forms.NumberInput(attrs={**_pricing_attrs}),
            "consumables_per_hour": forms.NumberInput(attrs={**_pricing_attrs}),
            "subcontracts": forms.NumberInput(attrs={**_pricing_attrs}),
            "contingency_pct": forms.NumberInput(attrs={**_pricing_attrs}),
            "utility_pct": forms.NumberInput(attrs={**_pricing_attrs}),
            "negotiation_pct": forms.NumberInput(attrs={**_pricing_attrs}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }


class ServiceActivityForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceActivity
        fields = [
            "service_template",
            "order",
            "name",
            "responsible_role",
            "estimated_hours",
            "description",
        ]
        widgets = {
            "service_template": forms.Select(attrs={"class": "form-select"}),
            "order": forms.NumberInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "responsible_role": forms.Select(attrs={"class": "form-select"}),
            "estimated_hours": forms.NumberInput(attrs={"class": "form-control"}),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class DeliverableForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Deliverable
        fields = ["service_template", "name", "unit", "order"]
