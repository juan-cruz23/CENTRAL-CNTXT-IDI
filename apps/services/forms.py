from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.services.models import Deliverable, Hardware, HardwareMaintenance, KeyActivity, ProjectCategory, ProjectPhase, ServiceActivity, ServiceSubCategory, ServiceTemplate, Software, SoftwarePayment


class ProjectCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectCategory
        fields = ["code", "name", "operative_line", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3}),
            "operative_line": forms.Select(attrs={"class": "select select-bordered w-full"}),
        }


class HardwareForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Hardware
        fields = [
            "name", "brand", "model_name", "serial_number", "location",
            "value", "depreciation_years", "depreciation_per_hour",
            "purchase_date", "warranty_expiration",
            "is_direct_cost", "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Ej. Workstation Alta Gama (opcional)"}),
            "purchase_date": forms.DateInput(attrs={"type": "date"}),
            "warranty_expiration": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ("value", "depreciation_per_hour"):
            self.fields[f].required = False

    def clean_value(self):
        return self.cleaned_data.get("value") or 0

    def clean_depreciation_per_hour(self):
        return self.cleaned_data.get("depreciation_per_hour") or 0


class HardwareMaintenanceForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = HardwareMaintenance
        fields = ["maintenance_type", "date", "cost", "provider", "description", "next_maintenance_date"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "next_maintenance_date": forms.DateInput(attrs={"type": "date"}),
            "description": forms.Textarea(attrs={"rows": 2}),
        }


class SoftwareForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Software
        fields = [
            "name", "vendor", "version", "license_type", "seats",
            "annual_value", "monthly_value", "hourly_value",
            "acquisition_date", "expiration_date", "auto_renewal", "is_direct_cost",
            "vendor_url", "notes", "is_active",
        ]
        widgets = {
            "acquisition_date": forms.DateInput(attrs={"type": "date"}),
            "expiration_date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ("annual_value", "monthly_value", "hourly_value"):
            self.fields[f].required = False

    def clean_annual_value(self):
        return self.cleaned_data.get("annual_value") or 0

    def clean_monthly_value(self):
        return self.cleaned_data.get("monthly_value") or 0

    def clean_hourly_value(self):
        return self.cleaned_data.get("hourly_value") or 0


class SoftwarePaymentForm(DaisyUIFormMixin, forms.ModelForm):
    new_expiration_date = forms.DateField(
        required=False,
        label="Actualizar vencimiento a",
        widget=forms.DateInput(attrs={"type": "date"}),
    )

    class Meta:
        model = SoftwarePayment
        fields = ["payment_date", "amount", "notes"]
        widgets = {
            "payment_date": forms.DateInput(attrs={"type": "date"}),
        }


class ProjectPhaseForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectPhase
        fields = ["number", "name", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ServiceSubCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceSubCategory
        fields = ["code", "name", "operative_line", "description", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ServiceTemplateForm(DaisyUIFormMixin, forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Aceptar decimales con coma (es-CO) o punto. Sin esto, la entrada
        # localizada del navegador "30,00" falla con "Ingrese un número".
        for field in self.fields.values():
            if isinstance(field, forms.DecimalField):
                field.localize = True
                field.widget.is_localized = True

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


class DeliverableInlineForm(forms.ModelForm):
    class Meta:
        model = Deliverable
        fields = ["name", "unit", "quantity"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered input-sm w-full", "placeholder": "Nombre del entregable"}),
            "unit": forms.TextInput(attrs={"class": "input input-bordered input-sm w-full", "placeholder": "Ej. Proyecto, Und, m2"}),
            "quantity": forms.NumberInput(attrs={"class": "input input-bordered input-sm w-full", "placeholder": "1", "step": "0.01", "min": "0"}),
        }


def deliverable_inline_formset(instance=None, data=None):
    from django.forms import inlineformset_factory
    DeliverableFormSet = inlineformset_factory(
        ServiceTemplate,
        Deliverable,
        form=DeliverableInlineForm,
        extra=0,
        can_delete=True,
    )
    if data:
        return DeliverableFormSet(data, instance=instance)
    return DeliverableFormSet(instance=instance)


class KeyActivityForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = KeyActivity
        fields = ["deliverable", "name", "order"]


class KeyActivityInlineForm(forms.ModelForm):
    class Meta:
        model = KeyActivity
        fields = ["name", "order"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered input-sm w-full", "placeholder": "Nombre de la actividad clave"}),
            "order": forms.NumberInput(attrs={"class": "input input-bordered input-sm w-20", "min": "1"}),
        }


class ServiceActionInlineForm(forms.ModelForm):
    class Meta:
        model = ServiceActivity
        fields = ["name", "order", "responsible_role", "estimated_hours"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "input input-bordered input-sm w-full", "placeholder": "Descripción de la acción"}),
            "order": forms.NumberInput(attrs={"class": "input input-bordered input-sm w-16", "min": "1"}),
            "responsible_role": forms.Select(attrs={"class": "select select-bordered select-sm w-full"}),
            "estimated_hours": forms.NumberInput(attrs={"class": "input input-bordered input-sm w-20", "step": "0.5", "min": "0"}),
        }


def keyactivity_inline_formset(instance=None, data=None, extra=1, prefix=None):
    from django.forms import inlineformset_factory
    FS = inlineformset_factory(Deliverable, KeyActivity, form=KeyActivityInlineForm, extra=extra, can_delete=True)
    kwargs = {"instance": instance}
    if prefix:
        kwargs["prefix"] = prefix
    return FS(data, **kwargs) if data else FS(**kwargs)


def action_inline_formset(instance=None, data=None, prefix=None, extra=1):
    from django.forms import inlineformset_factory
    FS = inlineformset_factory(KeyActivity, ServiceActivity, form=ServiceActionInlineForm, extra=extra, can_delete=True,
                               fk_name="key_activity")
    kwargs = {"instance": instance}
    if prefix:
        kwargs["prefix"] = prefix
    return FS(data, **kwargs) if data else FS(**kwargs)


class ServiceActivityForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ServiceActivity
        fields = ["service_template", "key_activity", "name", "responsible_role", "estimated_hours", "order", "description"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}
