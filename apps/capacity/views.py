from datetime import date

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from apps.capacity.forms import ProjectAllocationForm
from apps.capacity.models import CapacityAlert, ProjectAllocation, TeamMemberCapacity


class CapacityOverviewView(LoginRequiredMixin, TemplateView):
    """Shows team members with their current allocation percentages."""

    template_name = "capacity/overview.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        # Get current capacities for all users
        capacities = TeamMemberCapacity.objects.filter(
            effective_from__lte=today,
        ).filter(
            Q(effective_until__isnull=True) | Q(effective_until__gte=today),
        ).select_related("user")

        # Build overview data: each member with their total allocation
        overview = []
        for cap in capacities:
            allocations = ProjectAllocation.objects.filter(
                user=cap.user,
                start_date__lte=today,
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=today),
            )
            total_weekly_hours = allocations.aggregate(
                total=Sum("weekly_hours"),
            )["total"] or 0
            total_allocation_pct = allocations.aggregate(
                total=Sum("allocation_pct"),
            )["total"] or 0

            overview.append({
                "user": cap.user,
                "available_hours": cap.weekly_available_hours,
                "allocated_hours": total_weekly_hours,
                "allocation_pct": total_allocation_pct,
                "allocations": allocations.select_related("project", "role"),
            })

        context["overview"] = overview
        return context


class CapacityHeatmapView(LoginRequiredMixin, TemplateView):
    """Returns data for ECharts calendar heatmap (JSON endpoint + template)."""

    template_name = "capacity/heatmap.html"

    def get(self, request, *args, **kwargs):
        if request.headers.get("Accept") == "application/json":
            return self.get_json(request)
        return super().get(request, *args, **kwargs)

    def get_json(self, request):
        """Return allocation data as JSON for the ECharts heatmap."""
        allocations = ProjectAllocation.objects.select_related("user", "project").all()

        heatmap_data = []
        for alloc in allocations:
            heatmap_data.append({
                "user": str(alloc.user),
                "project": str(alloc.project),
                "start_date": alloc.start_date.isoformat(),
                "end_date": alloc.end_date.isoformat() if alloc.end_date else None,
                "weekly_hours": float(alloc.weekly_hours),
                "allocation_pct": float(alloc.allocation_pct),
            })

        return JsonResponse({"data": heatmap_data})


class AllocationMatrixView(LoginRequiredMixin, TemplateView):
    """Person-project matrix view showing allocation across the team."""

    template_name = "capacity/matrix.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()

        allocations = ProjectAllocation.objects.filter(
            start_date__lte=today,
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=today),
        ).select_related("user", "project")

        # Build matrix: users as rows, projects as columns
        users = {}
        projects = set()
        for alloc in allocations:
            user_key = alloc.user.pk
            if user_key not in users:
                users[user_key] = {
                    "user": alloc.user,
                    "projects": {},
                }
            users[user_key]["projects"][alloc.project.pk] = {
                "project": alloc.project,
                "weekly_hours": alloc.weekly_hours,
                "allocation_pct": alloc.allocation_pct,
            }
            projects.add(alloc.project)

        context["users"] = users.values()
        context["projects"] = sorted(projects, key=lambda p: p.code)
        return context


class CapacityAlertListView(LoginRequiredMixin, ListView):
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


class AllocationCreateView(LoginRequiredMixin, CreateView):
    """Form to create a new project allocation."""

    model = ProjectAllocation
    form_class = ProjectAllocationForm
    template_name = "capacity/allocate.html"
    success_url = reverse_lazy("capacity:overview")
