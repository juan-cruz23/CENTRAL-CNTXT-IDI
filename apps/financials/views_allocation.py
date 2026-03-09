from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, TemplateView

from apps.financials.models import CostAllocation, CostAllocationPeriod
from domain.financials.cost_allocation import CostAllocationEngine


class CostAllocationOverviewView(LoginRequiredMixin, TemplateView):
    """Overview of cost allocation periods."""

    template_name = "financials/cost_allocation_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["periods"] = CostAllocationPeriod.objects.all()
        return context


class CostAllocationRunView(LoginRequiredMixin, TemplateView):
    """Preview and execute cost allocation for a period."""

    template_name = "financials/cost_allocation_run.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = self.request.GET.get("period", "")
        if period:
            engine = CostAllocationEngine()
            context["preview"] = engine.allocate_period(period, dry_run=True)
        context["period"] = period
        return context

    def post(self, request, *args, **kwargs):
        period = request.POST.get("period", "")
        if not period:
            messages.error(request, "Debe seleccionar un periodo.")
            return redirect("financials:cost_allocation_overview")

        engine = CostAllocationEngine()
        result = engine.allocate_period(period, dry_run=False)

        if result.get("saved"):
            messages.success(
                request,
                f"Prorrateo ejecutado para {period}: "
                f"{len(result['projects'])} proyectos, "
                f"${result['total_costs']:,.0f} distribuidos.",
            )
        else:
            messages.warning(request, result.get("message", "No se pudo ejecutar."))

        return redirect("financials:cost_allocation_overview")


class CostAllocationDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a specific allocation period."""

    model = CostAllocationPeriod
    template_name = "financials/cost_allocation_detail.html"
    context_object_name = "period"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allocations"] = self.object.allocations.select_related(
            "project",
        ).order_by("-allocated_amount")
        return context
