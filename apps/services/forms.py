from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.services.models import ServiceActivity, ServiceTemplate


class ServiceTemplateForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceTemplate
        fields = [
            "code",
            "name",
            "category",
            "phase",
            "base_unit_price",
            "estimated_hours",
            "estimated_days",
            "target_margin_pct",
            "description",
            "is_active",
        ]
        widgets = {
            "code": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.Select(attrs={"class": "form-select"}),
            "phase": forms.Select(attrs={"class": "form-select"}),
            "base_unit_price": forms.NumberInput(attrs={"class": "form-control"}),
            "estimated_hours": forms.NumberInput(attrs={"class": "form-control"}),
            "estimated_days": forms.NumberInput(attrs={"class": "form-control"}),
            "target_margin_pct": forms.NumberInput(attrs={"class": "form-control"}),
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
