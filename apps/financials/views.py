from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs["project_pk"]
        context["payment_milestones"] = PaymentMilestone.objects.filter(
            project_id=project_pk
        )
        context["profitability_summaries"] = ProfitabilitySummary.objects.filter(
            project_id=project_pk
        )
        context["project_pk"] = project_pk
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
