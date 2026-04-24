from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.financials.models import ColombianHoliday, CostCenterMapping, CostCenterSubCategory, ExpenseCategory, ExpenseSubCategory, OperationalExpenseType, PaymentMilestone, ProfitabilitySummary


class PaymentMilestoneForm(DaisyUIFormMixin, forms.ModelForm):
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


class CostCenterMappingForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = CostCenterMapping
        fields = ["cost_center_code", "cost_center_name", "project", "business_unit"]
        widgets = {
            "cost_center_code": forms.TextInput(attrs={"readonly": True}),
            "cost_center_name": forms.TextInput(attrs={"readonly": True}),
            "project": forms.Select(),
            "business_unit": forms.Select(),
        }


class AccountingTransactionFilterForm(forms.Form):
    """Filter form for the accounting overview."""

    period = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input input-bordered input-sm w-28", "placeholder": "YYYY-MM"}),
    )
    account_code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input input-bordered input-sm w-32", "placeholder": "Cuenta"}),
    )
    cost_center = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input input-bordered input-sm w-32", "placeholder": "C. Costo"}),
    )
    third_party_nit = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={"class": "input input-bordered input-sm w-32", "placeholder": "NIT"}),
    )


class ProfitabilitySummaryForm(DaisyUIFormMixin, forms.ModelForm):
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


class ExpenseCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ExpenseCategory
        fields = ["code", "name", "category_type", "is_active"]


class ExpenseSubCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ExpenseSubCategory
        fields = ["category", "code", "name", "is_active"]


class OperationalExpenseTypeForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = OperationalExpenseType
        fields = ["subcategory", "name", "vendor", "monthly_reference", "is_active"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["monthly_reference"].required = False


class CostCenterSubCategoryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = CostCenterSubCategory
        fields = ["cost_center", "code", "name", "is_active"]


class ColombianHolidayForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ColombianHoliday
        fields = ["date", "name", "holiday_type"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["date"].input_formats = ["%Y-%m-%d"]
