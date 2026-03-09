from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.views import View
from django.views.generic import ListView, TemplateView

from apps.metrics.models import ProjectMetricSnapshot
from apps.projects.models import Project
from domain.metrics.calculators import SCurveGenerator


class ProjectMetricsView(LoginRequiredMixin, TemplateView):
    """
    Displays the latest EVM snapshot for a project, including
    SPI/CPI gauges and an S-Curve placeholder chart.
    """

    template_name = "metrics/project_metrics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        latest_snapshot = (
            ProjectMetricSnapshot.objects.filter(project=project)
            .order_by("-snapshot_date")
            .first()
        )

        context["project"] = project
        context["snapshot"] = latest_snapshot

        # Determine SPI/CPI status labels for gauge coloring
        if latest_snapshot:
            context["spi_status"] = _get_index_status(latest_snapshot.spi)
            context["cpi_status"] = _get_index_status(latest_snapshot.cpi)
        else:
            context["spi_status"] = "none"
            context["cpi_status"] = "none"

        return context


class SCurveDataView(LoginRequiredMixin, View):
    """
    Returns JSON data for rendering an S-Curve chart with ECharts.

    Response format:
    {
        "dates": ["2025-01-01", ...],
        "planned_value": [1000, ...],
        "earned_value": [900, ...],
        "actual_cost": [950, ...]
    }
    """

    def get(self, request, project_pk, *args, **kwargs):
        project = get_object_or_404(Project, pk=project_pk)
        start_date = request.GET.get("start_date")
        end_date = request.GET.get("end_date")
        mode = request.GET.get("mode", "cost")

        generator = SCurveGenerator(project)
        data = generator.generate(
            start_date=start_date, end_date=end_date, mode=mode,
        )

        return JsonResponse(data, safe=False)


class MetricHistoryView(LoginRequiredMixin, ListView):
    """
    Lists all metric snapshots for a project in reverse chronological order.
    """

    template_name = "metrics/metric_history.html"
    context_object_name = "snapshots"
    paginate_by = 30

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return ProjectMetricSnapshot.objects.filter(
            project=self.project
        ).order_by("-snapshot_date")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        return context


def _get_index_status(value):
    """
    Returns a status label based on an EVM performance index value.

    - 'critical': < 0.9 (significantly behind)
    - 'warning': 0.9 - 0.95 (slightly behind)
    - 'on_track': 0.95 - 1.05 (on target)
    - 'ahead': > 1.05 (ahead of plan)
    """
    if value < 0.9:
        return "critical"
    elif value < 0.95:
        return "warning"
    elif value <= 1.05:
        return "on_track"
    else:
        return "ahead"
