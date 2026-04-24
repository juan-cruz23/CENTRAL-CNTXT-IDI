from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, TemplateView, UpdateView

from apps.common.mixins import FinancialAccessMixin
from apps.financials.forms import (
    AccountingTransactionFilterForm,
    ColombianHolidayForm,
    CostCenterMappingForm,
    ExpenseCategoryForm,
    CostCenterSubCategoryForm,
    ExpenseSubCategoryForm,
    OperationalExpenseTypeForm,
    PaymentMilestoneForm,
)
from apps.financials.models import (
    AccountingTransaction,
    ColombianHoliday,
    CostCenterMapping,
    CostCenterSubCategory,
    ExpenseCategory,
    ExpenseSubCategory,
    OperationalExpenseType,
    PaymentMilestone,
    ProfitabilitySummary,
)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ProjectFinancialView(FinancialAccessMixin, TemplateView):
    """Vista general financiera de un proyecto: hitos de pago y rentabilidad."""

    template_name = "financials/project_financial.html"

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["financials/project_financial_partial.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs["project_pk"]
        context["payment_milestones"] = PaymentMilestone.objects.filter(
            project_id=project_pk
        )
        context["project_pk"] = project_pk

        # Auto-calculated profitability (Bloque 3b)
        from apps.projects.models import Project, ServiceInstance

        project = get_object_or_404(Project, pk=project_pk)
        payment_agg = PaymentMilestone.objects.filter(
            project_id=project_pk
        ).aggregate(
            total_invoiced=Coalesce(
                Sum("executed_value"),
                Value(Decimal("0")),
                output_field=DecimalField(),
            ),
            total_collected=Coalesce(
                Sum("collection_value"),
                Value(Decimal("0")),
                output_field=DecimalField(),
            ),
        )
        total_cost = ServiceInstance.objects.filter(
            project_id=project_pk
        ).aggregate(
            total=Coalesce(
                Sum("real_operative_cost"),
                Value(Decimal("0")),
                output_field=DecimalField(),
            ),
        )["total"]
        collected = payment_agg["total_collected"]
        utility = collected - total_cost
        if project.total_value and project.total_value > 0:
            margin_pct = (utility / project.total_value * 100).quantize(Decimal("0.01"))
        else:
            margin_pct = Decimal("0")

        context["profitability"] = {
            "total_value": project.total_value,
            "total_invoiced": payment_agg["total_invoiced"],
            "total_collected": collected,
            "total_cost": total_cost,
            "utility": utility,
            "margin_pct": margin_pct,
        }
        return context


class PaymentMilestoneListView(LoginRequiredMixin, ListView):
    model = PaymentMilestone
    template_name = "financials/paymentmilestone_list.html"
    context_object_name = "payment_milestones"

    def get_queryset(self):
        return PaymentMilestone.objects.filter(
            project_id=self.kwargs["project_pk"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        context["create_url"] = reverse(
            "financials:payment_create",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )
        return context


class PaymentMilestoneCreateView(LoginRequiredMixin, CreateView):
    model = PaymentMilestone
    form_class = PaymentMilestoneForm
    template_name = "financials/paymentmilestone_form.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["project"] = self.kwargs["project_pk"]
        return initial

    def get_success_url(self):
        return reverse(
            "financials:payment_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class PaymentMilestoneUpdateView(LoginRequiredMixin, UpdateView):
    model = PaymentMilestone
    form_class = PaymentMilestoneForm
    template_name = "financials/paymentmilestone_form.html"

    def get_success_url(self):
        return reverse(
            "financials:payment_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class PaymentMilestoneDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete a payment milestone."""

    def delete(self, request, project_pk, pk):
        pm = get_object_or_404(PaymentMilestone, pk=pk, project_id=project_pk)
        pm.delete()
        return HttpResponse("")


class CostCenterMappingListView(FinancialAccessMixin, ListView):
    """Lista de centros de costo con mapeo a proyectos/BU."""

    model = CostCenterMapping
    template_name = "financials/cost_center_mapping.html"
    context_object_name = "mappings"

    def get_queryset(self):
        return CostCenterMapping.objects.select_related(
            "project", "business_unit"
        ).order_by("cost_center_code")


class CostCenterMappingUpdateView(FinancialAccessMixin, UpdateView):
    """Actualizar mapeo de un centro de costo."""

    model = CostCenterMapping
    form_class = CostCenterMappingForm
    template_name = "financials/cost_center_mapping_form.html"

    def get_success_url(self):
        return reverse("financials:cost_center_mapping")


class AccountingOverviewView(FinancialAccessMixin, ListView):
    """Lista paginada de transacciones contables importadas de Loggro."""

    model = AccountingTransaction
    template_name = "financials/accounting_overview.html"
    context_object_name = "transactions"
    paginate_by = 50

    def get_queryset(self):
        qs = AccountingTransaction.objects.select_related(
            "account", "cost_center"
        ).order_by("-document_date")

        period = self.request.GET.get("period")
        if period:
            qs = qs.filter(period=period)

        account_code = self.request.GET.get("account_code")
        if account_code:
            qs = qs.filter(account__account_code__startswith=account_code)

        cost_center = self.request.GET.get("cost_center")
        if cost_center:
            qs = qs.filter(cost_center__cost_center_code__icontains=cost_center)

        third_party_nit = self.request.GET.get("third_party_nit")
        if third_party_nit:
            qs = qs.filter(third_party_nit__icontains=third_party_nit)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["filter_form"] = AccountingTransactionFilterForm(self.request.GET)
        return context


class ProfitabilityOverviewView(FinancialAccessMixin, ListView):
    """Vista general de rentabilidad de todos los proyectos."""

    model = ProfitabilitySummary
    template_name = "financials/profitability_overview.html"
    context_object_name = "profitability_summaries"


class RealProfitabilityView(FinancialAccessMixin, TemplateView):
    """Rentabilidad real basada en distribución de tiempo del equipo."""

    template_name = "financials/real_profitability.html"

    def get_context_data(self, **kwargs):
        from datetime import date
        from django.db.models import Sum
        from apps.projects.models import Project
        from apps.financials.models import CostAllocation, PaymentMilestone
        from domain.financials.time_cost_engine import get_project_profitability

        context = super().get_context_data(**kwargs)

        active_projects = Project.objects.filter(status="ACTIVE").order_by("code")
        profitability = []
        total_fee = Decimal("0")
        total_cost = Decimal("0")

        for project in active_projects:
            data = get_project_profitability(project.pk)
            profitability.append(data)
            total_fee += data["fee"]
            total_cost += data["total_cost"]

        total_utility = total_fee - total_cost
        total_margin = (
            (total_utility / total_fee * Decimal("100")).quantize(Decimal("0.01"))
            if total_fee > 0 else Decimal("0")
        )

        context["profitability"] = profitability
        context["totals"] = {
            "fee": total_fee,
            "cost": total_cost,
            "utility": total_utility,
            "margin_pct": total_margin,
        }

        # Available periods for recalculation
        from apps.financials.models import CostAllocationPeriod
        context["periods"] = CostAllocationPeriod.objects.filter(
            allocations__cost_type="OPERATIVE"
        ).distinct().order_by("-period")

        return context


class RecalculateCostsView(FinancialAccessMixin, View):
    """Recalculate cost allocations for a given month."""

    def post(self, request):
        from django.contrib import messages
        from domain.financials.time_cost_engine import save_month_allocations

        year = int(request.POST.get("year", 0))
        month = int(request.POST.get("month", 0))

        if not year or not month:
            messages.error(request, "Año y mes son requeridos.")
            return redirect("financials:real_profitability")

        result = save_month_allocations(year, month)
        if result["saved"]:
            messages.success(
                request,
                f"Costos recalculados para {result['period']}: "
                f"{len(result['projects'])} proyectos, "
                f"${float(result['total_cost']):,.0f} distribuidos.",
            )
        else:
            messages.warning(request, result.get("message", "Sin datos."))

        return redirect("financials:real_profitability")


# ---------------------------------------------------------------------------
# ExpenseCategory CRUD (Nivel 1)
# ---------------------------------------------------------------------------
class ExpenseCategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ExpenseCategory
    template_name = "financials/expense_category_list.html"
    context_object_name = "categories"

class ExpenseCategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = "financials/expense_category_form.html"
    success_url = reverse_lazy("financials:expense_category_list")

class ExpenseCategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ExpenseCategory
    form_class = ExpenseCategoryForm
    template_name = "financials/expense_category_form.html"
    success_url = reverse_lazy("financials:expense_category_list")

class ExpenseCategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ExpenseCategory
    template_name = "financials/expense_category_confirm_delete.html"
    success_url = reverse_lazy("financials:expense_category_list")


# ---------------------------------------------------------------------------
# ExpenseSubCategory CRUD (Nivel 2)
# ---------------------------------------------------------------------------
class ExpenseSubCategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ExpenseSubCategory
    template_name = "financials/expense_subcategory_list.html"
    context_object_name = "subcategories"

class ExpenseSubCategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ExpenseSubCategory
    form_class = ExpenseSubCategoryForm
    template_name = "financials/expense_subcategory_form.html"
    success_url = reverse_lazy("financials:expense_subcategory_list")

class ExpenseSubCategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ExpenseSubCategory
    form_class = ExpenseSubCategoryForm
    template_name = "financials/expense_subcategory_form.html"
    success_url = reverse_lazy("financials:expense_subcategory_list")

class ExpenseSubCategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ExpenseSubCategory
    template_name = "financials/expense_subcategory_confirm_delete.html"
    success_url = reverse_lazy("financials:expense_subcategory_list")


# ---------------------------------------------------------------------------
# CostCenterSubCategory CRUD
# ---------------------------------------------------------------------------
class CostCenterSubCategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = CostCenterSubCategory
    template_name = "financials/cost_center_subcategory_list.html"
    context_object_name = "subcategories"

    def get_queryset(self):
        return CostCenterSubCategory.objects.select_related("cost_center").order_by(
            "cost_center__cost_center_code", "code"
        )


class CostCenterSubCategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = CostCenterSubCategory
    form_class = CostCenterSubCategoryForm
    template_name = "financials/cost_center_subcategory_form.html"
    success_url = reverse_lazy("financials:cost_center_subcategory_list")


class CostCenterSubCategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = CostCenterSubCategory
    form_class = CostCenterSubCategoryForm
    template_name = "financials/cost_center_subcategory_form.html"
    success_url = reverse_lazy("financials:cost_center_subcategory_list")


class CostCenterSubCategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = CostCenterSubCategory
    template_name = "financials/cost_center_subcategory_confirm_delete.html"
    success_url = reverse_lazy("financials:cost_center_subcategory_list")


# ---------------------------------------------------------------------------
# OperationalExpenseType CRUD (Nivel 3 — Concepto)
# ---------------------------------------------------------------------------
class ExpenseTypeListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = OperationalExpenseType
    template_name = "financials/expense_type_list.html"
    context_object_name = "expense_types"

    def get_queryset(self):
        return (
            OperationalExpenseType.objects
            .select_related("subcategory__category")
            .order_by(
                "subcategory__category__code",
                "subcategory__code",
                "name",
            )
        )

class ExpenseTypeCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = OperationalExpenseType
    form_class = OperationalExpenseTypeForm
    template_name = "financials/expense_type_form.html"
    success_url = reverse_lazy("financials:expense_type_list")

class ExpenseTypeUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = OperationalExpenseType
    form_class = OperationalExpenseTypeForm
    template_name = "financials/expense_type_form.html"
    success_url = reverse_lazy("financials:expense_type_list")

class ExpenseTypeDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = OperationalExpenseType
    template_name = "financials/expense_type_confirm_delete.html"
    success_url = reverse_lazy("financials:expense_type_list")


# ---------------------------------------------------------------------------
# ColombianHoliday CRUD (Maestros)
# ---------------------------------------------------------------------------
class HolidayListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ColombianHoliday
    template_name = "financials/holiday_list.html"
    context_object_name = "holidays"
    ordering = ["date"]


class HolidayCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ColombianHoliday
    form_class = ColombianHolidayForm
    template_name = "financials/holiday_form.html"
    success_url = reverse_lazy("financials:holiday_list")


class HolidayUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ColombianHoliday
    form_class = ColombianHolidayForm
    template_name = "financials/holiday_form.html"
    success_url = reverse_lazy("financials:holiday_list")


class HolidayDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ColombianHoliday
    template_name = "financials/holiday_confirm_delete.html"
    success_url = reverse_lazy("financials:holiday_list")
