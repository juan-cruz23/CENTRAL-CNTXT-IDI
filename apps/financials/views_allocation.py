from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import DetailView, TemplateView

from apps.common.mixins import FinancialAccessMixin
from apps.financials.models import CostAllocationPeriod, LineAllocationWeight
from apps.organizations.models import BusinessUnit
from domain.financials.cost_allocation import CostAllocationEngine, _period_to_quarter


class CostAllocationOverviewView(FinancialAccessMixin, TemplateView):
    template_name = "financials/cost_allocation_overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["periods"] = CostAllocationPeriod.objects.all()

        # Quarters that already have manual weights configured
        configured_quarters = (
            LineAllocationWeight.objects.values_list("quarter", flat=True)
            .distinct()
            .order_by("-quarter")
        )
        context["configured_quarters"] = list(configured_quarters)
        return context


class CostAllocationRunView(FinancialAccessMixin, TemplateView):
    template_name = "financials/cost_allocation_run.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        period = self.request.GET.get("period", "")
        if period:
            engine = CostAllocationEngine()
            context["preview"] = engine.allocate_period(period, dry_run=True)
            context["quarter"] = _period_to_quarter(period)
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


class CostAllocationDetailView(FinancialAccessMixin, DetailView):
    model = CostAllocationPeriod
    template_name = "financials/cost_allocation_detail.html"
    context_object_name = "period"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allocations"] = self.object.allocations.select_related(
            "project",
        ).order_by("-allocated_amount")
        return context


class LineWeightConfigView(FinancialAccessMixin, TemplateView):
    """Configure operative-line weights for a quarter, with auto-proposal."""

    template_name = "financials/line_weight_config.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        quarter = self.kwargs["quarter"]
        engine = CostAllocationEngine()

        # Existing saved weights (if any)
        saved = {
            w.business_unit.code: w
            for w in LineAllocationWeight.objects.filter(quarter=quarter).select_related(
                "business_unit"
            )
        }

        # Auto-proposal based on current hours
        proposals = engine.propose_line_weights(quarter)

        # Merge: for each line show saved value (editable) + proposed reference
        rows = []
        for p in proposals:
            saved_obj = saved.get(p["line_code"])
            rows.append({
                "line_id": p["line_id"],
                "line_code": p["line_code"],
                "line_name": p["line_name"],
                "proposed_pct": p["proposed_pct"],
                "hours": p["hours"],
                "saved_pct": float(saved_obj.weight_pct) if saved_obj else None,
            })

        context["quarter"] = quarter
        context["rows"] = rows
        context["has_saved"] = bool(saved)
        context["total_saved_pct"] = sum(float(w.weight_pct) for w in saved.values())
        return context

    def post(self, request, *args, **kwargs):
        quarter = self.kwargs["quarter"]
        lines = request.POST.getlist("line_id")
        pcts = request.POST.getlist("weight_pct")

        if not lines:
            messages.error(request, "No se recibieron datos.")
            return redirect("financials:line_weight_config", quarter=quarter)

        from decimal import Decimal, InvalidOperation

        total = Decimal("0")
        entries = []
        for line_id, pct_str in zip(lines, pcts):
            try:
                pct = Decimal(pct_str.replace(",", "."))
            except InvalidOperation:
                messages.error(request, f"Valor inválido: {pct_str}")
                return redirect("financials:line_weight_config", quarter=quarter)
            entries.append((line_id, pct))
            total += pct

        if abs(total - Decimal("100")) > Decimal("0.1"):
            messages.error(
                request,
                f"Los pesos deben sumar 100 %. Actualmente suman {total:.2f} %.",
            )
            return redirect("financials:line_weight_config", quarter=quarter)

        # Delete old and recreate
        LineAllocationWeight.objects.filter(quarter=quarter).delete()
        for line_id, pct in entries:
            bu = get_object_or_404(BusinessUnit, pk=line_id)
            LineAllocationWeight.objects.create(
                quarter=quarter,
                business_unit=bu,
                weight_pct=pct,
                is_manual=True,
            )

        messages.success(request, f"Pesos guardados para {quarter}.")
        return redirect("financials:cost_allocation_overview")
