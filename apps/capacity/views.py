from collections import defaultdict
from datetime import date, timedelta
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import HttpResponse, JsonResponse
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView, View

from apps.capacity.forms import ProjectAllocationForm
from apps.capacity.models import CapacityAlert, ProjectAllocation, TeamMemberCapacity
from apps.projects.models import Project, ServiceInstance


class CapacityContextMixin:
    """Adds pending_alerts count to every capacity view."""

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["pending_alerts"] = CapacityAlert.objects.filter(is_resolved=False).count()
        return context


class CapacityOverviewView(LoginRequiredMixin, CapacityContextMixin, TemplateView):
    """Shows team members with their current allocation percentages."""

    template_name = "capacity/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        DEFAULT_WEEKLY_HOURS = Decimal("40")

        from apps.accounts.models import User
        from apps.projects.models import ServiceInstanceAction

        # Profesionales activos con al menos un rol
        users = User.objects.filter(
            is_active=True,
            user_roles__isnull=False,
        ).distinct().prefetch_related("user_roles__role")

        # Mapeo capacidades configuradas
        cap_map = {
            c.user_id: c for c in TeamMemberCapacity.objects.filter(
                effective_from__lte=today,
            ).filter(
                Q(effective_until__isnull=True) | Q(effective_until__gte=today),
            )
        }

        overview = []
        total_available = Decimal("0")
        total_allocated = Decimal("0")
        overloaded_count = 0

        for user in users:
            # 1. Capacidad disponible (configurada o default)
            cap = cap_map.get(user.pk)
            avail = cap.weekly_available_hours if cap else DEFAULT_WEEKLY_HOURS
            has_capacity_config = cap is not None

            # 2. Alocaciones manuales activas (ProjectAllocation)
            allocs = ProjectAllocation.objects.filter(
                user=user,
                start_date__lte=today,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today),
            ).select_related("project", "role")
            alloc_hours = allocs.aggregate(total=Sum("weekly_hours"))["total"] or Decimal("0")

            # 3. Servicios del cronograma asignados (ServiceInstance)
            sis = ServiceInstance.objects.filter(
                assigned_professional=user,
            ).select_related("project", "responsible_role")
            schedule_planned = sis.aggregate(total=Sum("projected_hours"))["total"] or Decimal("0")
            schedule_actual = sis.aggregate(total=Sum("actual_hours"))["total"] or Decimal("0")

            # 4. Acciones del cronograma asignadas (ServiceInstanceAction)
            actions = ServiceInstanceAction.objects.filter(
                assigned_professional=user,
            ).select_related("service_instance__project")
            actions_planned = actions.aggregate(total=Sum("estimated_hours"))["total"] or Decimal("0")
            actions_actual = actions.aggregate(total=Sum("actual_hours"))["total"] or Decimal("0")

            # Total horas planeadas/reales en cronograma
            total_planned = schedule_planned + actions_planned
            total_actual = schedule_actual + actions_actual

            # Dedicación semanal (alocaciones manuales son weekly; cronograma es total y se mantiene aparte)
            pct = round((alloc_hours / avail * 100) if avail else 0)
            if pct > 100:
                overloaded_count += 1

            total_available += avail
            total_allocated += alloc_hours

            # Detalle por proyecto (combina alocaciones + servicios)
            details_by_project: dict[int, dict] = {}
            for alloc in allocs:
                k = alloc.project_id
                d = details_by_project.setdefault(k, {
                    "code": alloc.project.code,
                    "name": alloc.project.name,
                    "project_pk": alloc.project.pk,
                    "alloc_hours": Decimal("0"),
                    "planned_hours": Decimal("0"),
                    "actual_hours": Decimal("0"),
                    "services_count": 0,
                    "actions_count": 0,
                    "role": alloc.role.name if alloc.role else "",
                })
                d["alloc_hours"] += alloc.weekly_hours
            for si in sis:
                k = si.project_id
                d = details_by_project.setdefault(k, {
                    "code": si.project.code,
                    "name": si.project.name,
                    "project_pk": si.project.pk,
                    "alloc_hours": Decimal("0"),
                    "planned_hours": Decimal("0"),
                    "actual_hours": Decimal("0"),
                    "services_count": 0,
                    "actions_count": 0,
                    "role": si.responsible_role.name if si.responsible_role else "",
                })
                d["planned_hours"] += si.projected_hours or 0
                d["actual_hours"] += si.actual_hours or 0
                d["services_count"] += 1
            for act in actions:
                proj = act.service_instance.project
                k = proj.pk
                d = details_by_project.setdefault(k, {
                    "code": proj.code,
                    "name": proj.name,
                    "project_pk": proj.pk,
                    "alloc_hours": Decimal("0"),
                    "planned_hours": Decimal("0"),
                    "actual_hours": Decimal("0"),
                    "services_count": 0,
                    "actions_count": 0,
                    "role": "",
                })
                d["planned_hours"] += act.estimated_hours or 0
                d["actual_hours"] += act.actual_hours or 0
                d["actions_count"] += 1

            project_details = list(details_by_project.values())

            # Avance %: real / planeado en cronograma
            progress_pct = round((total_actual / total_planned * 100) if total_planned else 0)

            overview.append({
                "user": user,
                "has_capacity_config": has_capacity_config,
                "available_hours": int(avail),
                "allocated_hours": int(alloc_hours),
                "allocation_pct": pct,
                "schedule_planned": int(total_planned),
                "schedule_actual": int(total_actual),
                "progress_pct": progress_pct,
                "project_count": len(project_details),
                "project_details": project_details,
            })

        # Orden: con asignaciones primero, sobrecargados arriba
        overview.sort(key=lambda x: (-x["allocation_pct"], -x["schedule_planned"]))

        # KPI summary
        team_size = len(overview)
        avg_utilization = round(
            sum(item["allocation_pct"] for item in overview) / team_size
        ) if team_size else 0
        free_hours = int(total_available - total_allocated) if total_allocated < total_available else 0
        total_planned_kpi = sum(item["schedule_planned"] for item in overview)
        total_actual_kpi = sum(item["schedule_actual"] for item in overview)

        context["overview"] = overview
        context["kpi"] = {
            "team_size": team_size,
            "avg_utilization": avg_utilization,
            "overloaded": overloaded_count,
            "free_hours": free_hours,
            "schedule_planned": total_planned_kpi,
            "schedule_actual": total_actual_kpi,
        }
        context["active_tab"] = "overview"
        context["page_title"] = "Capacidad del Equipo"
        return context


class CapacityHeatmapView(LoginRequiredMixin, CapacityContextMixin, TemplateView):
    """Returns data for ECharts heatmap (JSON endpoint + template)."""

    template_name = "capacity/heatmap.html"

    def get(self, request, *args, **kwargs):
        if request.headers.get("Accept") == "application/json":
            return self.get_json(request)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "heatmap"
        context["page_title"] = "Mapa de Calor"
        return context

    def get_json(self, request):
        """Return {weeks, users, values, capacities} for ECharts heatmap.

        Combina tres fuentes de carga:
          - ProjectAllocation (alocaciones manuales con weekly_hours)
          - ServiceInstance (servicios del cronograma con projected_hours
            distribuidas en las semanas del rango)
          - ServiceInstanceAction (acciones asignadas a un profesional)
        """
        from apps.accounts.models import User
        from apps.projects.models import ServiceInstanceAction
        DEFAULT_HOURS = 40

        today = date.today()

        # Generate 16 weeks: 4 past + 12 future
        start_monday = today - timedelta(days=today.weekday()) - timedelta(weeks=4)
        weeks = [start_monday + timedelta(weeks=i) for i in range(16)]
        week_labels = [w.strftime("%d %b") for w in weeks]
        last_week_end = weeks[-1] + timedelta(days=6)

        # Capacidades configuradas
        cap_map = {
            c.user_id: int(c.weekly_available_hours)
            for c in TeamMemberCapacity.objects.filter(
                effective_from__lte=today,
            ).filter(
                Q(effective_until__isnull=True) | Q(effective_until__gte=today),
            )
        }

        # Construir lista de usuarios: todos los activos con rol
        users_qs = User.objects.filter(
            is_active=True,
            user_roles__isnull=False,
        ).distinct().order_by("first_name", "last_name")

        user_names = []
        user_ids = []
        user_caps = []
        user_set = {}
        for u in users_qs:
            user_set[u.pk] = len(user_names)
            user_names.append(u.get_full_name() or u.username)
            user_ids.append(u.pk)
            user_caps.append(cap_map.get(u.pk, DEFAULT_HOURS))

        # 1. Alocaciones manuales (ProjectAllocation)
        allocations = ProjectAllocation.objects.filter(
            start_date__lte=last_week_end,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=weeks[0]),
        ).select_related("user")

        # 2. ServiceInstance del cronograma con responsable y fechas
        sis = ServiceInstance.objects.filter(
            assigned_professional__isnull=False,
            projected_start_date__isnull=False,
            projected_end_date__isnull=False,
            projected_start_date__lte=last_week_end,
            projected_end_date__gte=weeks[0],
        ).select_related("assigned_professional", "project")

        # 3. ServiceInstanceAction asignadas (heredan fechas del ServiceInstance)
        actions = ServiceInstanceAction.objects.filter(
            assigned_professional__isnull=False,
            service_instance__projected_start_date__isnull=False,
            service_instance__projected_end_date__isnull=False,
            service_instance__projected_start_date__lte=last_week_end,
            service_instance__projected_end_date__gte=weeks[0],
        ).select_related("assigned_professional", "service_instance")

        # Asegurarse que usuarios asignados existan (aunque no tengan rol)
        for src in (allocations, sis, actions):
            for obj in src:
                u = obj.user if hasattr(obj, "user") else obj.assigned_professional
                if u and u.pk not in user_set:
                    user_set[u.pk] = len(user_names)
                    user_names.append(u.get_full_name() or u.username)
                    user_ids.append(u.pk)
                    user_caps.append(cap_map.get(u.pk, DEFAULT_HOURS))

        # Build heatmap grid: [week_idx, user_idx, hours]
        grid = defaultdict(float)

        # 1. Alocaciones manuales — weekly_hours fijas
        for alloc in allocations:
            uidx = user_set.get(alloc.user_id)
            if uidx is None:
                continue
            a_start = alloc.start_date
            a_end = alloc.end_date or last_week_end
            for wi, w in enumerate(weeks):
                w_end = w + timedelta(days=6)
                if a_start <= w_end and a_end >= w:
                    grid[(wi, uidx)] += float(alloc.weekly_hours)

        # 2. ServiceInstance — projected_hours distribuidas en las semanas del rango
        def distribute(start, end, total_hours, uidx):
            if not total_hours:
                return
            total_days = (end - start).days + 1
            if total_days <= 0:
                return
            hours_per_day = float(total_hours) / total_days
            for wi, w in enumerate(weeks):
                w_end = w + timedelta(days=6)
                ov_start = max(start, w)
                ov_end = min(end, w_end)
                if ov_start <= ov_end:
                    overlap_days = (ov_end - ov_start).days + 1
                    grid[(wi, uidx)] += hours_per_day * overlap_days

        for si in sis:
            uidx = user_set.get(si.assigned_professional_id)
            if uidx is None:
                continue
            distribute(si.projected_start_date, si.projected_end_date,
                       si.projected_hours, uidx)

        for act in actions:
            uidx = user_set.get(act.assigned_professional_id)
            if uidx is None:
                continue
            si = act.service_instance
            distribute(si.projected_start_date, si.projected_end_date,
                       act.estimated_hours, uidx)

        values = [[wi, ui, round(h, 1)] for (wi, ui), h in grid.items()]

        return JsonResponse({
            "weeks": week_labels,
            "week_dates": [w.isoformat() for w in weeks],
            "users": user_names,
            "user_ids": user_ids,
            "values": values,
            "capacities": user_caps,
        })


class AllocationMatrixView(LoginRequiredMixin, CapacityContextMixin, TemplateView):
    """Person-project matrix view showing allocation across the team."""

    template_name = "capacity/matrix.html"

    def get_context_data(self, **kwargs):
        from apps.accounts.models import User
        from apps.projects.models import Project, ServiceInstanceAction
        DEFAULT_HOURS = 40

        context = super().get_context_data(**kwargs)
        today = date.today()
        # Semana actual: lunes a domingo
        week_start = today - timedelta(days=today.weekday())
        week_end = week_start + timedelta(days=6)

        # Capacidades configuradas
        cap_map = {
            c.user_id: int(c.weekly_available_hours)
            for c in TeamMemberCapacity.objects.filter(
                effective_from__lte=today,
            ).filter(
                Q(effective_until__isnull=True) | Q(effective_until__gte=today),
            )
        }

        # Profesionales con rol activo
        users_qs = User.objects.filter(
            is_active=True,
            user_roles__isnull=False,
        ).distinct().order_by("first_name", "last_name")

        users: dict[int, dict] = {}
        for u in users_qs:
            users[u.pk] = {"user": u, "projects": {}}

        projects_set: dict[int, Project] = {}

        def add(user_id, project, hours):
            if not user_id or hours <= 0:
                return
            if user_id not in users:
                u = User.objects.filter(pk=user_id).first()
                if not u:
                    return
                users[user_id] = {"user": u, "projects": {}}
            users[user_id]["projects"][project.pk] = (
                users[user_id]["projects"].get(project.pk, 0) + hours
            )
            projects_set[project.pk] = project

        # 1. Alocaciones manuales activas hoy
        for alloc in ProjectAllocation.objects.filter(
            start_date__lte=week_end,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=week_start),
        ).select_related("user", "project"):
            add(alloc.user_id, alloc.project, float(alloc.weekly_hours))

        # Helper: prorratear horas totales a la semana actual
        def week_share(start, end, total_h):
            if not start or not end or not total_h:
                return 0.0
            total_days = (end - start).days + 1
            if total_days <= 0:
                return 0.0
            ov_start = max(start, week_start)
            ov_end = min(end, week_end)
            if ov_start > ov_end:
                return 0.0
            overlap = (ov_end - ov_start).days + 1
            return float(total_h) / total_days * overlap

        # 2. ServiceInstance del cronograma activos esta semana
        for si in ServiceInstance.objects.filter(
            assigned_professional__isnull=False,
            projected_start_date__lte=week_end,
            projected_end_date__gte=week_start,
        ).select_related("assigned_professional", "project"):
            h = week_share(si.projected_start_date, si.projected_end_date, si.projected_hours)
            add(si.assigned_professional_id, si.project, h)

        # 3. Acciones del cronograma activas esta semana
        for act in ServiceInstanceAction.objects.filter(
            assigned_professional__isnull=False,
            service_instance__projected_start_date__lte=week_end,
            service_instance__projected_end_date__gte=week_start,
        ).select_related("assigned_professional", "service_instance__project"):
            si = act.service_instance
            h = week_share(si.projected_start_date, si.projected_end_date, act.estimated_hours)
            add(act.assigned_professional_id, si.project, h)

        projects = sorted(projects_set.values(), key=lambda p: p.code)
        project_pks = [p.pk for p in projects]

        matrix = []
        for user_data in sorted(users.values(), key=lambda u: (u["user"].first_name or "", u["user"].last_name or "")):
            cells = []
            total = 0.0
            for pk in project_pks:
                hours = user_data["projects"].get(pk, 0)
                cells.append({"hours": round(hours, 1) if hours else 0})
                total += hours
            available = cap_map.get(user_data["user"].pk, DEFAULT_HOURS)
            free = available - total
            matrix.append({
                "user": user_data["user"],
                "cells": cells,
                "total_hours": round(total, 1),
                "available_hours": available,
                "free_hours": round(free, 1),
                "overloaded": total > available,
                "has_capacity_config": user_data["user"].pk in cap_map,
            })

        context["matrix"] = matrix
        context["projects"] = projects
        context["week_start"] = week_start
        context["week_end"] = week_end
        context["active_tab"] = "matrix"
        context["page_title"] = "Matriz de Asignación"
        return context


class CapacityAlertListView(LoginRequiredMixin, CapacityContextMixin, ListView):
    """List of unresolved capacity alerts."""

    model = CapacityAlert
    template_name = "capacity/alerts.html"
    context_object_name = "alerts"
    paginate_by = 25

    def get_queryset(self):
        return (
            CapacityAlert.objects.filter(is_resolved=False)
            .select_related("user")
            .order_by("-week_start")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "alerts"
        context["page_title"] = "Alertas de Capacidad"
        return context


class AllocationCreateView(LoginRequiredMixin, CapacityContextMixin, CreateView):
    """Form to create a new project allocation."""

    model = ProjectAllocation
    form_class = ProjectAllocationForm
    template_name = "capacity/allocate.html"

    def get_success_url(self):
        project_pk = self.request.GET.get("project")
        if project_pk:
            from django.urls import reverse
            return reverse("projects:detail", kwargs={"pk": project_pk})
        return reverse_lazy("capacity:overview")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["initial_project"] = self.request.GET.get("project")
        return kwargs

    def form_valid(self, form):
        response = super().form_valid(form)
        # Check for overload and add warning message
        from domain.capacity.services import AllocationService

        result = AllocationService.validate_new_allocation(
            user_id=self.object.user_id,
            weekly_hours=float(self.object.weekly_hours),
            start_date=self.object.start_date,
        )
        if result["would_overload"]:
            messages.warning(self.request, result["warning_message"])
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["active_tab"] = "allocate"
        context["page_title"] = "Asignar Recurso"

        # If coming from a project, show project name
        project_pk = self.request.GET.get("project")
        if project_pk:
            try:
                context["for_project"] = Project.objects.get(pk=project_pk)
            except Project.DoesNotExist:
                pass

        # Current load summary for reference
        today = date.today()
        summary = []
        for cap in TeamMemberCapacity.objects.filter(
            effective_from__lte=today,
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=today),
        ).select_related("user").order_by("user__first_name"):
            alloc_hours = ProjectAllocation.objects.filter(
                user=cap.user,
                start_date__lte=today,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today),
            ).aggregate(total=Sum("weekly_hours"))["total"] or 0
            free = int(cap.weekly_available_hours) - int(alloc_hours)
            summary.append({
                "user": cap.user,
                "available": int(cap.weekly_available_hours),
                "allocated": int(alloc_hours),
                "free": free,
                "overloaded": free < 0,
            })
        context["load_summary"] = summary
        return context


class ProjectTeamView(LoginRequiredMixin, TemplateView):
    """HTMX partial: shows team allocations for a specific project."""

    template_name = "capacity/_project_team.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.kwargs["project_pk"]
        today = date.today()

        allocations = ProjectAllocation.objects.filter(
            project_id=project_pk,
            start_date__lte=today,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today),
        ).select_related("user", "role").order_by("user__first_name")

        # Build a map of user_id -> assigned ServiceInstances for this project
        assigned_services = ServiceInstance.objects.filter(
            project_id=project_pk,
            assigned_professional__isnull=False,
        ).select_related("assigned_professional", "phase_instance")
        user_services_map = defaultdict(list)
        for si in assigned_services:
            user_services_map[si.assigned_professional_id].append({
                "pk": si.pk,
                "code": si.code,
                "name": si.name,
                "progress_pct": float(si.progress_pct or 0),
                "projected_hours": float(si.projected_hours or 0),
                "project_pk": project_pk,
                "phase_pk": si.phase_instance_id,
            })

        # Enrich with capacity data
        team = []
        for alloc in allocations:
            cap = TeamMemberCapacity.objects.filter(
                user=alloc.user,
                effective_from__lte=today,
            ).filter(
                Q(effective_until__isnull=True) | Q(effective_until__gte=today),
            ).first()
            total_alloc = ProjectAllocation.objects.filter(
                user=alloc.user,
                start_date__lte=today,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today),
            ).aggregate(total=Sum("weekly_hours"))["total"] or 0
            available = int(cap.weekly_available_hours) if cap else 40
            team.append({
                "user": alloc.user,
                "role": alloc.role,
                "hours_this_project": int(alloc.weekly_hours),
                "total_allocated": int(total_alloc),
                "available": available,
                "pct": round(int(total_alloc) / available * 100) if available else 0,
                "start_date": alloc.start_date,
                "end_date": alloc.end_date,
                "services": user_services_map.get(alloc.user_id, []),
            })

        context["team"] = team
        context["project_pk"] = project_pk

        # Roles requeridos según servicios del cronograma (para mostrar cuando no hay equipo)
        from collections import defaultdict as _dd
        role_data = _dd(lambda: {"role": None, "hours": 0, "services": 0, "professionals": set()})
        schedule_sis = ServiceInstance.objects.filter(
            project_id=project_pk,
            phase_instance__isnull=True,
            responsible_role__isnull=False,
        ).select_related("responsible_role", "assigned_professional")
        for si in schedule_sis:
            r = si.responsible_role
            role_data[r.pk]["role"] = r
            role_data[r.pk]["hours"] += float(si.projected_hours or 0)
            role_data[r.pk]["services"] += 1
            if si.assigned_professional:
                role_data[r.pk]["professionals"].add(si.assigned_professional)
        # Convert sets to sorted lists for template
        required_roles = []
        for entry in sorted(role_data.values(), key=lambda x: -x["hours"]):
            entry["professionals"] = sorted(entry["professionals"], key=lambda u: u.get_full_name())
            required_roles.append(entry)
        context["required_roles"] = required_roles

        return context


class ServiceInstanceOptionsView(LoginRequiredMixin, TemplateView):
    """HTMX partial: returns service instance <option> tags filtered by project."""

    template_name = "capacity/_service_instance_options.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project_pk = self.request.GET.get("project")
        services = []
        if project_pk:
            services = ServiceInstance.objects.filter(
                project_id=project_pk,
            ).order_by("code")
        context["services"] = services
        return context


class HeatmapDrilldownView(LoginRequiredMixin, View):
    """HTMX endpoint: returns detail of a user's allocations for a specific week."""

    def get(self, request):
        from apps.accounts.models import User

        user_id = request.GET.get("user_id")
        week_date = request.GET.get("week")
        if not user_id or not week_date:
            return HttpResponse("")

        try:
            user_id = int(user_id)
            from datetime import datetime
            week_start = datetime.strptime(week_date, "%Y-%m-%d").date()
        except (ValueError, TypeError):
            return HttpResponse("")

        week_end = week_start + timedelta(days=6)
        user = User.objects.filter(pk=user_id).first()
        if not user:
            return HttpResponse("")

        from apps.projects.models import ServiceInstanceAction

        # Capacidad
        cap = TeamMemberCapacity.objects.filter(
            user_id=user_id,
            effective_from__lte=week_start,
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=week_start),
        ).first()
        available_hours = int(cap.weekly_available_hours) if cap else 40

        # Construye detalle por proyecto desde 3 fuentes
        project_details: dict[int, dict] = {}
        total_hours = 0.0

        # 1. Alocaciones manuales activas en la semana
        allocations = ProjectAllocation.objects.filter(
            user_id=user_id,
            start_date__lte=week_end,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=week_start),
        ).select_related("project", "role")
        for alloc in allocations:
            d = project_details.setdefault(alloc.project_id, {
                "project_code": alloc.project.code,
                "project_name": alloc.project.name,
                "role": alloc.role.name if alloc.role else "",
                "hours": 0.0,
                "services": [],
            })
            d["hours"] += float(alloc.weekly_hours)
            total_hours += float(alloc.weekly_hours)

        # Helper: prorratear horas de un servicio a la semana indicada
        def week_share(start, end, total_h):
            if not start or not end or not total_h:
                return 0.0
            total_days = (end - start).days + 1
            if total_days <= 0:
                return 0.0
            ov_start = max(start, week_start)
            ov_end = min(end, week_end)
            if ov_start > ov_end:
                return 0.0
            overlap = (ov_end - ov_start).days + 1
            return float(total_h) / total_days * overlap

        # 2. ServiceInstance del cronograma activos en esta semana
        sis = ServiceInstance.objects.filter(
            assigned_professional_id=user_id,
            projected_start_date__lte=week_end,
            projected_end_date__gte=week_start,
        ).select_related("project")
        for si in sis:
            h = week_share(si.projected_start_date, si.projected_end_date, si.projected_hours)
            if h <= 0:
                continue
            d = project_details.setdefault(si.project_id, {
                "project_code": si.project.code,
                "project_name": si.project.name,
                "role": "",
                "hours": 0.0,
                "services": [],
            })
            d["hours"] += h
            d["services"].append({
                "code": si.code,
                "name": si.name,
                "progress": float(si.progress_pct or 0),
            })
            total_hours += h

        # 3. Acciones asignadas que caigan en esta semana
        actions = ServiceInstanceAction.objects.filter(
            assigned_professional_id=user_id,
            service_instance__projected_start_date__lte=week_end,
            service_instance__projected_end_date__gte=week_start,
        ).select_related("service_instance__project")
        for act in actions:
            si = act.service_instance
            h = week_share(si.projected_start_date, si.projected_end_date, act.estimated_hours)
            if h <= 0:
                continue
            d = project_details.setdefault(si.project_id, {
                "project_code": si.project.code,
                "project_name": si.project.name,
                "role": "",
                "hours": 0.0,
                "services": [],
            })
            d["hours"] += h
            total_hours += h

        # Render: redondear horas y volver a lista
        for d in project_details.values():
            d["hours"] = round(d["hours"], 1)
        project_details = list(project_details.values())
        total_hours = round(total_hours, 1)

        return TemplateResponse(
            request,
            "capacity/_heatmap_drilldown.html",
            {
                "user_name": user.get_full_name() or user.username,
                "week_start": week_start,
                "week_end": week_end,
                "project_details": project_details,
                "total_hours": total_hours,
                "available_hours": available_hours,
                "utilization_pct": round(total_hours / available_hours * 100) if available_hours else 0,
                "any_data": bool(project_details),
            },
        )


class ValidateAllocationView(LoginRequiredMixin, View):
    """HTMX endpoint: check if new allocation would cause overload."""

    def get(self, request):
        user_id = request.GET.get("user")
        weekly_hours = request.GET.get("weekly_hours")
        if not user_id or not weekly_hours:
            return HttpResponse("")

        try:
            user_id = int(user_id)
            weekly_hours = float(weekly_hours)
        except (ValueError, TypeError):
            return HttpResponse("")

        from domain.capacity.services import AllocationService

        result = AllocationService.validate_new_allocation(user_id, weekly_hours)

        if not result["would_overload"]:
            return HttpResponse("")

        return TemplateResponse(
            request,
            "capacity/_allocation_warning.html",
            {
                "warning": result["warning_message"],
                "current_allocated": result["current_allocated"],
                "new_total": result["new_total"],
                "available": result["available"],
            },
        )
