from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, DecimalField, F, Q, Sum, Value
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import DetailView, TemplateView

from apps.metrics.models import ProjectMetricSnapshot
from apps.organizations.models import OrganizationalSystem
from apps.projects.models import (
    Milestone,
    Project,
    ProjectPhaseInstance,
    ServiceInstance,
)


# ---------------------------------------------------------------------------
# Executive Dashboard
# ---------------------------------------------------------------------------
class ExecutiveDashboardView(LoginRequiredMixin, TemplateView):
    """
    Top-level executive dashboard showing portfolio-wide KPIs,
    project health indicators, risk alerts and active project summaries.
    """

    template_name = "dashboards/home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        active_projects = Project.objects.filter(status=Project.Status.ACTIVE)

        # ------------------------------------------------------------------
        # Portfolio-wide KPIs
        # ------------------------------------------------------------------
        context["active_projects"] = active_projects.count()

        context["total_portfolio_value"] = active_projects.aggregate(
            total=Coalesce(
                Sum("total_value"),
                Value(Decimal("0")),
                output_field=DecimalField(),
            )
        )["total"]

        context["avg_progress"] = active_projects.aggregate(
            avg=Coalesce(
                Avg("current_progress_pct"),
                Value(Decimal("0")),
                output_field=DecimalField(),
            )
        )["avg"]

        # ------------------------------------------------------------------
        # Average SPI / CPI from each project's latest metric snapshot
        # ------------------------------------------------------------------
        latest_snapshots = self._get_latest_snapshots(active_projects)

        if latest_snapshots.exists():
            agg = latest_snapshots.aggregate(
                avg_spi=Coalesce(
                    Avg("spi"),
                    Value(Decimal("0")),
                    output_field=DecimalField(),
                ),
                avg_cpi=Coalesce(
                    Avg("cpi"),
                    Value(Decimal("0")),
                    output_field=DecimalField(),
                ),
            )
            context["avg_spi"] = agg["avg_spi"]
            context["avg_cpi"] = agg["avg_cpi"]
        else:
            context["avg_spi"] = Decimal("0")
            context["avg_cpi"] = Decimal("0")

        # ------------------------------------------------------------------
        # Projects at risk: latest SPI < 0.9 or CPI < 0.9
        # ------------------------------------------------------------------
        at_risk_ids = latest_snapshots.filter(
            Q(spi__lt=Decimal("0.9")) | Q(cpi__lt=Decimal("0.9"))
        ).values_list("project_id", flat=True)
        at_risk_qs = active_projects.filter(
            pk__in=at_risk_ids
        ).select_related("client", "leader")
        context["projects_at_risk"] = at_risk_qs
        context["projects_at_risk_count"] = at_risk_qs.count()

        # ------------------------------------------------------------------
        # Recent alerts (5 most recent unread)
        # ------------------------------------------------------------------
        try:
            from apps.notifications.models import Alert

            context["recent_alerts"] = Alert.objects.filter(
                is_read=False
            ).order_by("-created_at")[:5]
        except (ImportError, Exception):
            context["recent_alerts"] = []

        # ------------------------------------------------------------------
        # Active projects with annotations for the summary table
        # ------------------------------------------------------------------
        context["projects"] = active_projects.select_related(
            "client", "leader", "category", "operative_line"
        ).annotate(
            service_count=Count("service_instances"),
        )

        context["create_url"] = reverse_lazy("projects:create")

        return context

    @staticmethod
    def _get_latest_snapshots(projects_qs):
        """
        Return a queryset of the most recent ProjectMetricSnapshot
        for each project in the given queryset.
        """
        from django.db.models import Max

        latest_dates = (
            ProjectMetricSnapshot.objects.filter(
                project__in=projects_qs,
            )
            .values("project")
            .annotate(latest_date=Max("snapshot_date"))
        )

        q_filter = Q()
        for entry in latest_dates:
            q_filter |= Q(
                project_id=entry["project"],
                snapshot_date=entry["latest_date"],
            )

        if not q_filter:
            return ProjectMetricSnapshot.objects.none()

        return ProjectMetricSnapshot.objects.filter(q_filter)


# ---------------------------------------------------------------------------
# Portfolio Dashboard
# ---------------------------------------------------------------------------
class PortfolioDashboardView(LoginRequiredMixin, TemplateView):
    """
    Full portfolio view powered by an AG Grid table.
    The actual data is loaded via the portfolio_data_api endpoint.
    """

    template_name = "dashboards/portfolio.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["projects"] = (
            Project.objects.select_related("client", "leader")
            .all()
            .order_by("-created_at")
        )
        return context


# ---------------------------------------------------------------------------
# Project Dashboard
# ---------------------------------------------------------------------------
class ProjectDashboardView(LoginRequiredMixin, DetailView):
    """
    Detailed dashboard for a single project showing phases, services,
    metric snapshots, payment milestones and satisfaction scores.
    """

    model = Project
    pk_url_kwarg = "project_pk"
    template_name = "dashboards/project.html"
    context_object_name = "project"

    def get_queryset(self):
        return Project.objects.select_related(
            "client", "leader", "category", "operative_line", "business_unit"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # ------------------------------------------------------------------
        # Phases with their service instances
        # ------------------------------------------------------------------
        context["phases"] = (
            ProjectPhaseInstance.objects.filter(project=project)
            .select_related("phase")
            .prefetch_related(
                "service_instances",
                "service_instances__assigned_professional",
                "service_instances__responsible_role",
            )
            .order_by("order")
        )

        # ------------------------------------------------------------------
        # Latest metric snapshot
        # ------------------------------------------------------------------
        context["latest_snapshot"] = (
            ProjectMetricSnapshot.objects.filter(project=project)
            .order_by("-snapshot_date")
            .first()
        )

        # ------------------------------------------------------------------
        # Payment milestones summary
        # ------------------------------------------------------------------
        try:
            from apps.financials.models import PaymentMilestone

            milestones = PaymentMilestone.objects.filter(project=project)
            context["payment_milestones"] = milestones.order_by("billing_date")
            context["payment_summary"] = milestones.aggregate(
                total_proposed=Coalesce(
                    Sum("proposed_value"),
                    Value(Decimal("0")),
                    output_field=DecimalField(),
                ),
                total_executed=Coalesce(
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
        except (ImportError, Exception):
            context["payment_milestones"] = []
            context["payment_summary"] = {
                "total_proposed": Decimal("0"),
                "total_executed": Decimal("0"),
                "total_collected": Decimal("0"),
            }

        # ------------------------------------------------------------------
        # Satisfaction scores
        # ------------------------------------------------------------------
        try:
            from apps.satisfaction.models import SatisfactionSurvey

            context["satisfaction"] = (
                SatisfactionSurvey.objects.filter(project=project)
                .order_by("-created_at")
                .first()
            )
        except (ImportError, Exception):
            context["satisfaction"] = None

        return context


# ---------------------------------------------------------------------------
# System Dashboard
# ---------------------------------------------------------------------------
class SystemDashboardView(LoginRequiredMixin, TemplateView):
    """
    Dashboard filtered by organizational system code (NEO, RED, etc.).
    Shows projects and metrics relevant to a specific organizational system.
    """

    template_name = "dashboards/system.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        system_code = self.kwargs["system_code"]

        system = get_object_or_404(OrganizationalSystem, code=system_code)
        context["system"] = system

        # Projects associated with the system via business unit or
        # operative line relationships
        context["projects"] = (
            Project.objects.filter(
                Q(business_unit__in=system.code)
                | Q(operative_line__business_unit__code=system.code)
            )
            .select_related("client", "leader")
            .distinct()
            if hasattr(system, "business_units")
            else Project.objects.none()
        )

        # Fallback: show all active projects when the system doesn't have
        # a direct business-unit relationship
        if not context["projects"].exists():
            context["projects"] = Project.objects.filter(
                status=Project.Status.ACTIVE
            ).select_related("client", "leader")

        return context


# ---------------------------------------------------------------------------
# Leader Dashboard
# ---------------------------------------------------------------------------
class LeaderDashboardView(LoginRequiredMixin, TemplateView):
    """
    Personal dashboard for a project leader showing their projects,
    team capacity, and upcoming milestones.
    """

    template_name = "dashboards/leader.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # ------------------------------------------------------------------
        # Projects led by the current user
        # ------------------------------------------------------------------
        context["my_projects"] = (
            Project.objects.filter(leader=user)
            .select_related("client", "category")
            .order_by("-created_at")
        )

        # ------------------------------------------------------------------
        # Team capacity: professionals assigned to the leader's projects
        # ------------------------------------------------------------------
        try:
            from apps.capacity.models import ProjectAllocation, TeamMemberCapacity

            project_ids = context["my_projects"].values_list("pk", flat=True)

            allocations = (
                ProjectAllocation.objects.filter(project_id__in=project_ids)
                .select_related("user", "project", "role")
                .order_by("user__first_name")
            )
            context["team_allocations"] = allocations

            team_user_ids = allocations.values_list("user_id", flat=True).distinct()
            context["team_capacity"] = (
                TeamMemberCapacity.objects.filter(user_id__in=team_user_ids)
                .select_related("user")
                .order_by("user__first_name")
            )
        except (ImportError, Exception):
            context["team_allocations"] = []
            context["team_capacity"] = []

        # ------------------------------------------------------------------
        # Upcoming milestones for the leader's projects
        # ------------------------------------------------------------------
        from datetime import date

        context["upcoming_milestones"] = (
            Milestone.objects.filter(
                project__in=context["my_projects"],
                planned_date__gte=date.today(),
            )
            .select_related("project", "phase_instance")
            .order_by("planned_date")[:15]
        )

        return context


# ---------------------------------------------------------------------------
# API: Portfolio data for AG Grid
# ---------------------------------------------------------------------------
@login_required
def portfolio_data_api(request):
    """
    Return JSON array of project summaries for AG Grid rendering.

    Each entry contains: code, name, client, status, progress, spi, cpi,
    total_value, leader, deviation.
    """
    projects = (
        Project.objects.select_related("client", "leader")
        .all()
        .order_by("code")
    )

    # Prefetch latest metric snapshot per project
    from django.db.models import Max, Subquery, OuterRef

    latest_snapshot_date = (
        ProjectMetricSnapshot.objects.filter(project=OuterRef("pk"))
        .order_by("-snapshot_date")
        .values("snapshot_date")[:1]
    )

    projects = projects.annotate(
        _latest_snapshot_date=Subquery(latest_snapshot_date),
    )

    # Build a lookup of latest snapshots
    snapshot_lookup = {}
    snapshot_project_ids = list(projects.values_list("pk", flat=True))
    if snapshot_project_ids:
        for snap in ProjectMetricSnapshot.objects.raw(
            """
            SELECT ms.*
            FROM metrics_projectmetricsnapshot ms
            INNER JOIN (
                SELECT project_id, MAX(snapshot_date) AS max_date
                FROM metrics_projectmetricsnapshot
                GROUP BY project_id
            ) latest ON ms.project_id = latest.project_id
                     AND ms.snapshot_date = latest.max_date
            """
        ):
            snapshot_lookup[snap.project_id] = snap

    data = []
    for project in projects:
        snapshot = snapshot_lookup.get(project.pk)
        data.append(
            {
                "code": project.code,
                "name": project.name,
                "client": project.client.name if project.client else "",
                "status": project.get_status_display(),
                "progress": float(project.current_progress_pct),
                "spi": float(snapshot.spi) if snapshot else None,
                "cpi": float(snapshot.cpi) if snapshot else None,
                "total_value": float(project.total_value),
                "leader": str(project.leader) if project.leader else "",
                "deviation": float(project.schedule_deviation_pct),
            }
        )

    return JsonResponse(data, safe=False)


# ---------------------------------------------------------------------------
# API: Cashflow data for ECharts
# ---------------------------------------------------------------------------
@login_required
def cashflow_data_api(request, project_pk):
    """
    Return JSON with payment milestone data for an ECharts bar chart.

    Response format:
    {
        "labels": ["Concepto 1", "Concepto 2", ...],
        "proposed": [1000000, 2000000, ...],
        "executed": [900000, 1800000, ...],
        "collected": [800000, 1700000, ...]
    }
    """
    project = get_object_or_404(Project, pk=project_pk)

    labels = []
    proposed = []
    executed = []
    collected = []

    try:
        from apps.financials.models import PaymentMilestone

        milestones = (
            PaymentMilestone.objects.filter(project=project)
            .order_by("billing_date", "pk")
        )

        for ms in milestones:
            labels.append(ms.concept if hasattr(ms, "concept") else str(ms))
            proposed.append(
                float(ms.proposed_value) if hasattr(ms, "proposed_value") else 0
            )
            executed.append(
                float(ms.executed_value) if hasattr(ms, "executed_value") else 0
            )
            collected.append(
                float(ms.collection_value)
                if hasattr(ms, "collection_value")
                else 0
            )
    except (ImportError, Exception):
        pass

    return JsonResponse(
        {
            "labels": labels,
            "proposed": proposed,
            "executed": executed,
            "collected": collected,
        }
    )
