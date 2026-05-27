from datetime import date
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Avg, Count, DecimalField, F, OuterRef, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import DetailView, TemplateView

from apps.metrics.models import ProjectMetricSnapshot
from apps.organizations.models import OrganizationalSystem
from apps.projects.models import (
    Milestone,
    Project,
    ProjectPhaseInstance,
    ServiceInstance,
)
from domain.financials.services import CashFlowService


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

        # Apply filters
        status_filter = self.request.GET.get("status")
        if status_filter:
            active_projects = Project.objects.filter(status=status_filter)

        tp_filter = self.request.GET.get("third_party") or self.request.GET.get("client")
        if tp_filter:
            active_projects = active_projects.filter(third_party_id=tp_filter)

        bu_filter = self.request.GET.get("bu")
        if bu_filter:
            active_projects = active_projects.filter(business_unit__code=bu_filter)

        context["current_status"] = status_filter or ""
        context["current_bu"] = bu_filter or ""
        context["status_choices"] = Project.Status.choices

        try:
            from apps.organizations.models import BusinessUnit
            context["business_units"] = BusinessUnit.objects.all()
        except Exception:
            context["business_units"] = []

        try:
            from apps.terceros.models import ThirdParty
            context["third_parties"] = ThirdParty.objects.filter(is_active=True).order_by("name")
        except Exception:
            context["third_parties"] = []

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
        ).select_related("third_party", "leader")
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
        latest_snap_sub = ProjectMetricSnapshot.objects.filter(
            project=OuterRef("pk")
        ).order_by("-snapshot_date")

        context["projects"] = active_projects.select_related(
            "third_party", "leader", "category", "operative_line"
        ).annotate(
            service_count=Count("service_instances"),
            latest_spi=Subquery(latest_snap_sub.values("spi")[:1]),
            latest_cpi=Subquery(latest_snap_sub.values("cpi")[:1]),
        )

        context["create_url"] = reverse_lazy("projects:create")

        # ------------------------------------------------------------------
        # Feed personalizado por rol
        # ------------------------------------------------------------------
        user = self.request.user

        # ¿Es líder de proyecto?
        try:
            context["user_is_project_leader"] = user.user_roles.filter(
                role__is_leader=True
            ).exists()
        except Exception:
            context["user_is_project_leader"] = False

        # Proyectos propios (cuando no es staff ni tiene acceso total)
        try:
            can_see_all = user.is_staff or user.user_roles.filter(
                role__can_access_all_projects=True
            ).exists()
            if not can_see_all:
                from django.db.models import Count, Subquery, OuterRef
                latest_snap_sub2 = ProjectMetricSnapshot.objects.filter(
                    project=OuterRef("pk")
                ).order_by("-snapshot_date")
                context["projects"] = Project.objects.filter(
                    leader=user
                ).select_related(
                    "third_party", "leader", "category", "operative_line"
                ).annotate(
                    service_count=Count("service_instances"),
                    latest_spi=Subquery(latest_snap_sub2.values("spi")[:1]),
                    latest_cpi=Subquery(latest_snap_sub2.values("cpi")[:1]),
                )
        except Exception:
            pass

        # Hitos próximos del líder (30 días)
        try:
            from apps.projects.models import Milestone
            context["upcoming_milestones"] = (
                Milestone.objects.filter(
                    project__leader=user,
                    planned_date__gte=date.today(),
                    actual_date__isnull=True,
                )
                .select_related("project", "project__third_party")
                .order_by("planned_date")[:8]
            )
        except Exception:
            context["upcoming_milestones"] = []

        # Tareas asignadas al usuario (LP e INT)
        try:
            from apps.projects.models import ServiceInstanceAction
            context["my_actions"] = (
                ServiceInstanceAction.objects.filter(
                    assigned_professional=user,
                    is_completed=False,
                )
                .select_related(
                    "service_instance__project",
                    "service_instance__project__third_party",
                    "responsible_role",
                )
                .order_by("service_instance__projected_end_date")[:10]
            )
        except Exception:
            context["my_actions"] = []

        # Estado del reporte semanal (INT)
        try:
            import datetime as dt
            from apps.timetracking.models import WeeklyTimeDistribution
            today_date = date.today()
            week_start = today_date - dt.timedelta(days=today_date.weekday())
            my_week = WeeklyTimeDistribution.objects.filter(
                user=user, week_start=week_start
            ).prefetch_related("entries").first()
            context["my_week_status"] = my_week.status if my_week else None
            context["my_week_pct"] = (
                sum(e.percentage for e in my_week.entries.all())
                if my_week else 0
            )
        except Exception:
            context["my_week_status"] = None
            context["my_week_pct"] = 0

        # Alertas filtradas por usuario / proyectos propios
        try:
            from apps.notifications.models import Alert
            from django.db.models import Q
            if user.is_staff:
                context["recent_alerts"] = Alert.objects.filter(
                    is_read=False
                ).order_by("-created_at")[:5]
            else:
                own_projects = Project.objects.filter(leader=user).values_list("pk", flat=True)
                context["recent_alerts"] = Alert.objects.filter(
                    Q(target_users=user) | Q(project__in=own_projects)
                ).distinct().order_by("-created_at")[:5]
        except Exception:
            context["recent_alerts"] = []

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
            Project.objects.select_related("third_party", "leader")
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
            "third_party", "leader", "category", "operative_line", "business_unit"
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # ------------------------------------------------------------------
        # Phases with their service instances (ProjectPhaseInstance)
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
        # Cronograma services (phase_instance=None) grouped by template phase
        # ------------------------------------------------------------------
        loose = list(
            ServiceInstance.objects.filter(project=project, phase_instance=None)
            .select_related(
                "service_template__phase",
                "assigned_professional",
                "responsible_role",
            )
            .order_by("service_template__phase__number", "projected_start_date", "code")
        )
        phase_groups_dict = {}
        for si in loose:
            phase = si.service_template.phase if si.service_template else None
            sort_key = (
                phase.number if phase and hasattr(phase, "number") else 999,
                phase.pk if phase else 0,
            )
            if sort_key not in phase_groups_dict:
                phase_groups_dict[sort_key] = {"phase": phase, "services": []}
            phase_groups_dict[sort_key]["services"].append(si)
        context["schedule_phase_groups"] = [
            v for _, v in sorted(phase_groups_dict.items())
        ]

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
            .select_related("third_party", "leader")
            .distinct()
            if hasattr(system, "business_units")
            else Project.objects.none()
        )

        # Fallback: show all active projects when the system doesn't have
        # a direct business-unit relationship
        if not context["projects"].exists():
            context["projects"] = Project.objects.filter(
                status=Project.Status.ACTIVE
            ).select_related("third_party", "leader")

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
            .select_related("third_party", "category")
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
# Recalculate Metrics (Bloque 7)
# ---------------------------------------------------------------------------
class RecalculateMetricsView(LoginRequiredMixin, View):
    """Recalculate EVM metrics for a project and create a new snapshot."""

    def post(self, request, project_pk):
        project = get_object_or_404(Project, pk=project_pk)
        from domain.metrics.calculators import EVMCalculator

        calculator = EVMCalculator(project)
        snapshot = calculator.create_snapshot()

        # Also update project-level metrics
        metrics = calculator.calculate()
        project.current_progress_pct = metrics["overall_progress_pct"]
        project.schedule_deviation_pct = metrics["schedule_deviation_pct"]
        project.profitability_pct = metrics["projected_margin_pct"]
        project.save(update_fields=[
            "current_progress_pct",
            "schedule_deviation_pct",
            "profitability_pct",
        ])

        if request.headers.get("HX-Request"):
            return HttpResponse(
                f'<div class="alert alert-success alert-sm">'
                f'<span>Métricas recalculadas. SPI={snapshot.spi}, CPI={snapshot.cpi}</span>'
                f'</div>'
            )
        messages.success(request, f"Métricas recalculadas para {project.code}.")
        return redirect("dashboards:project", project_pk=project_pk)


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
        Project.objects.select_related("third_party", "leader")
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
                "client": project.third_party.name if project.third_party else "",
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


# ---------------------------------------------------------------------------
# API: Periodic Cashflow (monthly, not per-milestone)
# ---------------------------------------------------------------------------
@login_required
def periodic_cashflow_api(request, project_pk):
    """Return monthly cash flow data for a project."""
    get_object_or_404(Project, pk=project_pk)
    data = CashFlowService.get_periodic_cashflow(project_id=project_pk)
    return JsonResponse(data)


@login_required
def company_cashflow_api(request):
    """Return aggregated cash flow for the whole company."""
    data = CashFlowService.get_periodic_cashflow()
    return JsonResponse(data)


@login_required
def bu_cashflow_api(request, bu_code):
    """Return cash flow aggregated by business unit."""
    data = CashFlowService.get_periodic_cashflow(business_unit_code=bu_code)
    return JsonResponse(data)


# ---------------------------------------------------------------------------
# API: Gantt Chart Data
# ---------------------------------------------------------------------------
@login_required
def gantt_data_api(request):
    """
    Timeline data for ECharts Gantt chart.
    Returns list of projects with start/end dates and progress.
    """
    projects = Project.objects.filter(
        status=Project.Status.ACTIVE
    ).order_by("planned_start_date")

    data = []
    for p in projects:
        data.append({
            "name": f"{p.code} - {p.name}",
            "start": p.planned_start_date.isoformat() if p.planned_start_date else None,
            "end": p.planned_end_date.isoformat() if p.planned_end_date else None,
            "progress": float(p.current_progress_pct),
            "status": p.status,
        })

    return JsonResponse(data, safe=False)


# ---------------------------------------------------------------------------
# API: Project Gantt (phases + services)
# ---------------------------------------------------------------------------
@login_required
def project_gantt_api(request, project_pk):
    """
    Gantt data for a single project — collapsible tree.
    Returns `items` list: level 0=phase, 1=service, 2=action.
    Service items are expandable; actions have no date bars (text only).
    """
    from apps.projects.models import ServiceInstanceAction, Milestone as MilestoneModel

    project = get_object_or_404(Project, pk=project_pk)
    items = []
    uid = 0

    def new_item(label, level, parent_id, s_start=None, s_end=None,
                 a_start=None, a_end=None, progress=0,
                 has_children=False, itype="phase", meta=None):
        nonlocal uid
        items.append({
            "id": uid,
            "label": label,
            "level": level,
            "parent_id": parent_id,
            "s_start": s_start.isoformat() if s_start else None,
            "s_end":   s_end.isoformat()   if s_end   else None,
            "a_start": a_start.isoformat() if a_start else None,
            "a_end":   a_end.isoformat()   if a_end   else None,
            "progress": float(progress),
            "has_children": has_children,
            "type": itype,
            **(meta or {}),
        })
        current = uid
        uid += 1
        return current

    def add_service(svc, phase_item_id):
        """Add a service item + its action children."""
        actions = list(
            ServiceInstanceAction.objects.filter(service_instance=svc)
            .select_related(
                "service_activity__key_activity__deliverable",
                "responsible_role",
                "assigned_professional",
            )
            .order_by("order")
        )
        has_actions = bool(actions)
        svc_id = new_item(
            label    = f"{svc.code} — {svc.name[:45]}",
            level    = 1,
            parent_id= phase_item_id,
            s_start  = svc.projected_start_date,
            s_end    = svc.projected_end_date,
            a_start  = svc.actual_start_date,
            a_end    = svc.actual_end_date,
            progress = svc.progress_pct or 0,
            has_children = has_actions,
            itype    = "service",
        )
        # Group actions by deliverable → key_activity
        seen_delivs = {}
        seen_kacts  = {}
        for act in actions:
            sa = act.service_activity
            d_name  = (sa.key_activity.deliverable.name if sa and sa.key_activity and sa.key_activity.deliverable else "Sin entregable")
            ka_name = (sa.key_activity.name if sa and sa.key_activity else "Sin actividad")
            role_code = act.responsible_role.code if act.responsible_role else "—"
            resp_name = act.assigned_professional.get_full_name() if act.assigned_professional else "Sin asignar"

            # Deliverable header (level 2)
            if d_name not in seen_delivs:
                seen_delivs[d_name] = new_item(
                    label=f"📦 {d_name}",
                    level=2, parent_id=svc_id,
                    has_children=True, itype="deliverable",
                )
                seen_kacts[d_name] = {}

            d_id = seen_delivs[d_name]

            # Key activity sub-header (level 3)
            kact_key = f"{d_name}||{ka_name}"
            if kact_key not in seen_kacts[d_name]:
                seen_kacts[d_name][kact_key] = new_item(
                    label=f"  ◆ {ka_name}",
                    level=3, parent_id=d_id,
                    has_children=True, itype="key_activity",
                )

            ka_id = seen_kacts[d_name][kact_key]

            # Action row (level 4)
            new_item(
                label=f"    {act.order}. {act.name[:50]}  [{role_code}] {resp_name}  {act.estimated_hours}h",
                level=4, parent_id=ka_id,
                has_children=False, itype="action",
            )

    # ── 1. Phase instances (ProjectPhaseInstance) ────────────────────────
    for phase in ProjectPhaseInstance.objects.filter(
        project=project
    ).select_related("phase").order_by("order"):
        starts = [s.projected_start_date for s in phase.service_instances.all() if s.projected_start_date]
        ends   = [s.projected_end_date   for s in phase.service_instances.all() if s.projected_end_date]
        ph_id  = new_item(
            label    = phase.phase.name,
            level    = 0,
            parent_id= None,
            s_start  = phase.planned_start_date or (min(starts) if starts else None),
            s_end    = phase.planned_end_date   or (max(ends)   if ends   else None),
            a_start  = phase.actual_start_date,
            a_end    = phase.actual_end_date,
            progress = phase.progress_pct,
            has_children = True,
            itype    = "phase",
        )
        for svc in ServiceInstance.objects.filter(
            project=project, phase_instance=phase
        ).order_by("code"):
            add_service(svc, ph_id)

    # ── 2. Loose services (phase_instance=None) grouped by template phase ─
    loose = list(
        ServiceInstance.objects.filter(project=project, phase_instance=None)
        .select_related("service_template__phase")
        .order_by("service_template__phase__number", "projected_start_date", "code")
    )
    if loose:
        phase_groups: dict = {}
        for svc in loose:
            ph    = svc.service_template.phase if svc.service_template else None
            key   = (ph.number if ph else 999, ph.pk if ph else 0)
            if key not in phase_groups:
                phase_groups[key] = {"phase": ph, "services": []}
            phase_groups[key]["services"].append(svc)

        for _, grp in sorted(phase_groups.items()):
            ph   = grp["phase"]
            svcs = grp["services"]
            starts = [s.projected_start_date for s in svcs if s.projected_start_date]
            ends   = [s.projected_end_date   for s in svcs if s.projected_end_date]
            ph_id  = new_item(
                label    = ph.name if ph else "Sin Fase",
                level    = 0,
                parent_id= None,
                s_start  = min(starts) if starts else None,
                s_end    = max(ends)   if ends   else None,
                has_children = True,
                itype    = "phase",
            )
            for svc in svcs:
                add_service(svc, ph_id)

    # ── 3. Hitos ─────────────────────────────────────────────────────────
    milestones_data = []
    for m in MilestoneModel.objects.filter(project=project).order_by("planned_date"):
        if m.planned_date:
            milestones_data.append({
                "name": m.name,
                "date": m.planned_date.isoformat(),
                "actual_date": m.actual_date.isoformat() if m.actual_date else None,
                "type": m.milestone_type,
            })

    return JsonResponse({
        "items": items,
        "milestones": milestones_data,
        "project_start": project.planned_start_date.isoformat() if project.planned_start_date else None,
        "project_end":   project.planned_end_date.isoformat()   if project.planned_end_date   else None,
    })


# ---------------------------------------------------------------------------
# API: Portfolio by Business Unit
# ---------------------------------------------------------------------------
@login_required
def portfolio_by_bu_api(request):
    """Portfolio value grouped by Business Unit."""
    from apps.organizations.models import BusinessUnit

    data = []
    for bu in BusinessUnit.objects.all():
        agg = Project.objects.filter(
            business_unit=bu, status=Project.Status.ACTIVE,
        ).aggregate(
            total=Coalesce(
                Sum("total_value"),
                Value(Decimal("0")),
                output_field=DecimalField(),
            ),
            count=Count("id"),
        )
        data.append({
            "name": bu.name,
            "code": bu.code,
            "total_value": float(agg["total"]),
            "project_count": agg["count"],
        })

    return JsonResponse(data, safe=False)
