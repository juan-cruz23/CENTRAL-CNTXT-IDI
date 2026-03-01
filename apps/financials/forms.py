from django import forms

from apps.financials.models import PaymentMilestone, ProfitabilitySummary


class PaymentMilestoneForm(forms.ModelForm):
    class Meta:
        model = PaymentMilestone
        fields = [
            "project",
            "concept",
            "proposed_value",
            "iva_value",
            "incidence_pct",
            "status",
            "discount_pct",
            "discount_value",
            "executed_value",
            "billing_date",
            "invoice_number",
            "invoice_value",
            "collection_value",
            "collection_date",
            "notes",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "concept": forms.TextInput(attrs={"class": "form-control"}),
            "proposed_value": forms.NumberInput(attrs={"class": "form-control"}),
            "iva_value": forms.NumberInput(attrs={"class": "form-control"}),
            "incidence_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "discount_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "discount_value": forms.NumberInput(attrs={"class": "form-control"}),
            "executed_value": forms.NumberInput(attrs={"class": "form-control"}),
            "billing_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "invoice_number": forms.TextInput(attrs={"class": "form-control"}),
            "invoice_value": forms.NumberInput(attrs={"class": "form-control"}),
            "collection_value": forms.NumberInput(attrs={"class": "form-control"}),
            "collection_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ProfitabilitySummaryForm(forms.ModelForm):
    class Meta:
        model = ProfitabilitySummary
        fields = [
            "project",
            "milestone_name",
            "value",
            "months_invested",
            "analysis_costs",
            "total_costs",
            "expenses",
            "cost_plus_expenses_monthly",
            "cost_plus_expenses_total",
            "revenue",
            "utility",
            "margin_pct",
            "utility_monthly",
            "margin_monthly_pct",
            "is_verified",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "milestone_name": forms.TextInput(attrs={"class": "form-control"}),
            "value": forms.NumberInput(attrs={"class": "form-control"}),
            "months_invested": forms.NumberInput(attrs={"class": "form-control"}),
            "analysis_costs": forms.NumberInput(attrs={"class": "form-control"}),
            "total_costs": forms.NumberInput(attrs={"class": "form-control"}),
            "expenses": forms.NumberInput(attrs={"class": "form-control"}),
            "cost_plus_expenses_monthly": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "cost_plus_expenses_total": forms.NumberInput(
                attrs={"class": "form-control"}
            ),
            "revenue": forms.NumberInput(attrs={"class": "form-control"}),
            "utility": forms.NumberInput(attrs={"class": "form-control"}),
            "margin_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "utility_monthly": forms.NumberInput(attrs={"class": "form-control"}),
            "margin_monthly_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "is_verified": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }
