from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import DecimalField, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.financials.forms import (
    AccountingTransactionFilterForm,
    CostCenterMappingForm,
    PaymentMilestoneForm,
)
from apps.financials.models import (
    AccountingTransaction,
    CostCenterMapping,
    PaymentMilestone,
    ProfitabilitySummary,
)


class ProjectFinancialView(LoginRequiredMixin, TemplateView):
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


class CostCenterMappingListView(LoginRequiredMixin, ListView):
    """Lista de centros de costo con mapeo a proyectos/BU."""

    model = CostCenterMapping
    template_name = "financials/cost_center_mapping.html"
    context_object_name = "mappings"

    def get_queryset(self):
        return CostCenterMapping.objects.select_related(
            "project", "business_unit"
        ).order_by("cost_center_code")


class CostCenterMappingUpdateView(LoginRequiredMixin, UpdateView):
    """Actualizar mapeo de un centro de costo."""

    model = CostCenterMapping
    form_class = CostCenterMappingForm
    template_name = "financials/cost_center_mapping_form.html"

    def get_success_url(self):
        return reverse("financials:cost_center_mapping")


class AccountingOverviewView(LoginRequiredMixin, ListView):
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


class ProfitabilityOverviewView(LoginRequiredMixin, ListView):
    """Vista general de rentabilidad de todos los proyectos."""

    model = ProfitabilitySummary
    template_name = "financials/profitability_overview.html"
    context_object_name = "profitability_summaries"
