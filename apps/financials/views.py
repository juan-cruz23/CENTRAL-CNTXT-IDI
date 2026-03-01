from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse
from django.views.generic import CreateView, ListView, TemplateView, UpdateView

from apps.financials.forms import PaymentMilestoneForm
from apps.financials.models import PaymentMilestone, ProfitabilitySummary


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


class ProfitabilityOverviewView(LoginRequiredMixin, ListView):
    """Vista general de rentabilidad de todos los proyectos."""

    model = ProfitabilitySummary
    template_name = "financials/profitability_overview.html"
    context_object_name = "profitability_summaries"
