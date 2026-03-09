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

        capacities = TeamMemberCapacity.objects.filter(
            effective_from__lte=today,
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=today),
        ).select_related("user")

        overview = []
        total_available = Decimal("0")
        total_allocated = Decimal("0")
        overloaded_count = 0

        for cap in capacities:
            allocations = ProjectAllocation.objects.filter(
                user=cap.user,
                start_date__lte=today,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today),
            ).select_related("project", "role")

            alloc_hours = allocations.aggregate(total=Sum("weekly_hours"))["total"] or Decimal("0")
            avail = cap.weekly_available_hours
            pct = round((alloc_hours / avail * 100) if avail else 0)

            if pct > 100:
                overloaded_count += 1

            total_available += avail
            total_allocated += alloc_hours

            # Build project detail list for expandable row
            project_details = []
            for alloc in allocations:
                project_details.append({
                    "code": alloc.project.code,
                    "name": alloc.project.name,
                    "role": alloc.role.name if alloc.role else "-",
                    "hours": int(alloc.weekly_hours),
                    "project_pk": alloc.project.pk,
                })

            overview.append({
                "user": cap.user,
                "available_hours": int(avail),
                "allocated_hours": int(alloc_hours),
                "allocation_pct": pct,
                "project_count": len(project_details),
                "project_details": project_details,
            })

        # Sort: overloaded first, then by allocation descending
        overview.sort(key=lambda x: -x["allocation_pct"])

        # KPI summary
        team_size = len(overview)
        avg_utilization = round(
            sum(item["allocation_pct"] for item in overview) / team_size
        ) if team_size else 0
        free_hours = int(total_available - total_allocated) if total_allocated < total_available else 0

        context["overview"] = overview
        context["kpi"] = {
            "team_size": team_size,
            "avg_utilization": avg_utilization,
            "overloaded": overloaded_count,
            "free_hours": free_hours,
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
        """Return {weeks, users, values, capacities} for ECharts heatmap."""
        today = date.today()
        allocations = ProjectAllocation.objects.filter(
            start_date__lte=today + timedelta(weeks=12),
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today - timedelta(weeks=4)),
        ).select_related("user", "project")

        if not allocations.exists():
            return JsonResponse({"weeks": [], "users": [], "values": [], "capacities": []})

        # Generate 16 weeks: 4 past + 12 future
        start_monday = today - timedelta(days=today.weekday()) - timedelta(weeks=4)
        weeks = [start_monday + timedelta(weeks=i) for i in range(16)]
        week_labels = [w.strftime("%d %b") for w in weeks]

        # Collect users preserving order from capacities
        capacities = TeamMemberCapacity.objects.filter(
            effective_from__lte=today,
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=today),
        ).select_related("user").order_by("user__first_name")

        user_names = []
        user_set = {}
        user_caps = []
        for cap in capacities:
            if cap.user.pk not in user_set:
                user_set[cap.user.pk] = len(user_names)
                user_names.append(cap.user.get_full_name() or cap.user.username)
                user_caps.append(int(cap.weekly_available_hours))

        # Add any allocated users not in capacities
        for alloc in allocations:
            if alloc.user.pk not in user_set:
                user_set[alloc.user.pk] = len(user_names)
                user_names.append(alloc.user.get_full_name() or alloc.user.username)
                user_caps.append(40)  # default

        # Build heatmap grid: [week_idx, user_idx, hours]
        grid = defaultdict(float)
        for alloc in allocations:
            if alloc.user.pk not in user_set:
                continue
            user_idx = user_set[alloc.user.pk]
            a_start = alloc.start_date
            a_end = alloc.end_date or (today + timedelta(weeks=12))
            for wi, w in enumerate(weeks):
                w_end = w + timedelta(days=6)
                if a_start <= w_end and a_end >= w:
                    grid[(wi, user_idx)] += float(alloc.weekly_hours)

        values = [[wi, ui, round(h, 1)] for (wi, ui), h in grid.items()]

        return JsonResponse({
            "weeks": week_labels,
            "users": user_names,
            "values": values,
            "capacities": user_caps,
        })


class AllocationMatrixView(LoginRequiredMixin, CapacityContextMixin, TemplateView):
    """Person-project matrix view showing allocation across the team."""

    template_name = "capacity/matrix.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        # Get capacities for the "available" column
        cap_map = {}
        for cap in TeamMemberCapacity.objects.filter(
            effective_from__lte=today,
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=today),
        ).select_related("user"):
            cap_map[cap.user.pk] = int(cap.weekly_available_hours)

        allocations = ProjectAllocation.objects.filter(
            start_date__lte=today,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today),
        ).select_related("user", "project")

        users = {}
        projects_set = set()
        for alloc in allocations:
            user_key = alloc.user.pk
            if user_key not in users:
                users[user_key] = {
                    "user": alloc.user,
                    "projects": {},
                }
            proj_key = alloc.project.pk
            if proj_key not in users[user_key]["projects"]:
                users[user_key]["projects"][proj_key] = 0
            users[user_key]["projects"][proj_key] += float(alloc.weekly_hours)
            projects_set.add(alloc.project)

        projects = sorted(projects_set, key=lambda p: p.code)
        project_pks = [p.pk for p in projects]

        matrix = []
        for user_data in sorted(users.values(), key=lambda u: u["user"].first_name):
            cells = []
            total = 0
            for pk in project_pks:
                hours = user_data["projects"].get(pk, 0)
                cells.append({"hours": int(hours) if hours == int(hours) else hours})
                total += hours
            available = cap_map.get(user_data["user"].pk, 40)
            free = available - total
            matrix.append({
                "user": user_data["user"],
                "cells": cells,
                "total_hours": int(total),
                "available_hours": available,
                "free_hours": int(free),
                "overloaded": total > available,
            })

        context["matrix"] = matrix
        context["projects"] = projects
        context["active_tab"] = "matrix"
        context["page_title"] = "Matriz de Asignacion"
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
