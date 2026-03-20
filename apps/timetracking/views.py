from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import ListView, TemplateView, View

from apps.projects.models import Project
from apps.timetracking.models import TimeDistributionEntry, WeeklyTimeDistribution


def get_current_week_start():
    """Returns the Monday of the current week."""
    today = date.today()
    return today - timedelta(days=today.weekday())


class TimeDistributionWidgetView(LoginRequiredMixin, TemplateView):
    """Main widget for weekly time distribution."""

    template_name = "timetracking/widget.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        week_start = self.request.GET.get("week")
        if week_start:
            from datetime import datetime
            week_start = datetime.strptime(week_start, "%Y-%m-%d").date()
        else:
            week_start = get_current_week_start()

        week_end = week_start + timedelta(days=6)

        # Get or create distribution for this week
        distribution, created = WeeklyTimeDistribution.objects.get_or_create(
            user=self.request.user,
            week_start=week_start,
        )

        # Get active projects
        active_projects = Project.objects.filter(
            status="ACTIVE",
        ).order_by("code")

        # Get existing entries
        existing_entries = {
            e.project_id: e.percentage
            for e in distribution.entries.all()
        }

        # Pre-fill from previous week if new and empty
        if created and not existing_entries:
            prev_week = week_start - timedelta(weeks=1)
            prev_dist = WeeklyTimeDistribution.objects.filter(
                user=self.request.user,
                week_start=prev_week,
                status=WeeklyTimeDistribution.Status.SUBMITTED,
            ).first()
            if prev_dist:
                for entry in prev_dist.entries.all():
                    if entry.project.status == "ACTIVE":
                        existing_entries[entry.project_id] = entry.percentage

        # Build project list with percentages
        projects_with_pct = []
        for project in active_projects:
            projects_with_pct.append({
                "project": project,
                "percentage": existing_entries.get(project.pk, 0),
            })

        # Sort: projects with percentage first, then alphabetically
        projects_with_pct.sort(key=lambda x: (-x["percentage"], x["project"].code))

        total_pct = sum(p["percentage"] for p in projects_with_pct)

        context["distribution"] = distribution
        context["projects_with_pct"] = projects_with_pct
        context["total_pct"] = total_pct
        context["week_start"] = week_start
        context["week_end"] = week_end
        context["is_current_week"] = week_start == get_current_week_start()
        context["prev_week"] = (week_start - timedelta(weeks=1)).isoformat()
        context["next_week"] = (week_start + timedelta(weeks=1)).isoformat()
        context["is_submitted"] = distribution.status == WeeklyTimeDistribution.Status.SUBMITTED
        return context


class TimeDistributionHistoryView(LoginRequiredMixin, ListView):
    """History of submitted distributions."""

    model = WeeklyTimeDistribution
    template_name = "timetracking/history.html"
    context_object_name = "distributions"
    paginate_by = 12

    def get_queryset(self):
        return WeeklyTimeDistribution.objects.filter(
            user=self.request.user,
            status=WeeklyTimeDistribution.Status.SUBMITTED,
        ).prefetch_related("entries__project")


class TimeDistributionEditView(LoginRequiredMixin, TemplateView):
    """Edit a previously submitted distribution."""

    template_name = "timetracking/widget.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        dist = get_object_or_404(
            WeeklyTimeDistribution,
            pk=self.kwargs["pk"],
            user=self.request.user,
        )
        # Redirect to widget with week param
        context["redirect_week"] = dist.week_start.isoformat()
        return context

    def get(self, request, *args, **kwargs):
        dist = get_object_or_404(
            WeeklyTimeDistribution,
            pk=self.kwargs["pk"],
            user=request.user,
        )
        return redirect(f"/tiempos/?week={dist.week_start.isoformat()}")


class TimeDistributionSaveView(LoginRequiredMixin, View):
    """HTMX endpoint to save distribution entries (auto-save)."""

    def post(self, request):
        week_start_str = request.POST.get("week_start")
        if not week_start_str:
            return JsonResponse({"error": "week_start required"}, status=400)

        from datetime import datetime
        week_start = datetime.strptime(week_start_str, "%Y-%m-%d").date()

        distribution, _ = WeeklyTimeDistribution.objects.get_or_create(
            user=request.user,
            week_start=week_start,
        )

        # Clear existing entries
        distribution.entries.all().delete()

        # Save new entries
        total = 0
        for key, value in request.POST.items():
            if key.startswith("project_"):
                project_id = key.replace("project_", "")
                try:
                    pct = int(value)
                    if pct > 0:
                        TimeDistributionEntry.objects.create(
                            distribution=distribution,
                            project_id=project_id,
                            percentage=pct,
                        )
                        total += pct
                except (ValueError, TypeError):
                    pass

        return JsonResponse({"total": total, "valid": total == 100})


class TimeDistributionSubmitView(LoginRequiredMixin, View):
    """Submit the weekly distribution."""

    def post(self, request):
        week_start_str = request.POST.get("week_start")
        if not week_start_str:
            messages.error(request, "Semana no especificada.")
            return redirect("timetracking:widget")

        from datetime import datetime
        week_start = datetime.strptime(week_start_str, "%Y-%m-%d").date()

        distribution, _ = WeeklyTimeDistribution.objects.get_or_create(
            user=request.user,
            week_start=week_start,
        )

        # Save entries first
        distribution.entries.all().delete()
        total = 0
        for key, value in request.POST.items():
            if key.startswith("project_"):
                project_id = key.replace("project_", "")
                try:
                    pct = int(value)
                    if pct > 0:
                        TimeDistributionEntry.objects.create(
                            distribution=distribution,
                            project_id=project_id,
                            percentage=pct,
                        )
                        total += pct
                except (ValueError, TypeError):
                    pass

        if total != 100:
            messages.error(request, f"La distribución debe sumar 100%. Actualmente suma {total}%.")
            return redirect(f"/tiempos/?week={week_start.isoformat()}")

        distribution.status = WeeklyTimeDistribution.Status.SUBMITTED
        distribution.submitted_at = timezone.now()
        distribution.save()

        # Auto-recalculate month costs
        try:
            from domain.financials.time_cost_engine import save_month_allocations
            result = save_month_allocations(week_start.year, week_start.month)
            if result["saved"]:
                cost_str = f"${float(result['total_cost']):,.0f}"
                messages.success(
                    request,
                    f"Distribución enviada. Costos del mes actualizados: "
                    f"{len(result['projects'])} proyectos, {cost_str} distribuidos.",
                )
            else:
                messages.success(request, f"Distribución de la semana {week_start} enviada correctamente.")
        except Exception:
            messages.success(request, f"Distribución de la semana {week_start} enviada correctamente.")

        return redirect("timetracking:widget")


@login_required
def time_distribution_summary_api(request):
    """API endpoint for distribution summary data (for charts)."""
    user = request.user
    distributions = WeeklyTimeDistribution.objects.filter(
        user=user,
        status=WeeklyTimeDistribution.Status.SUBMITTED,
    ).prefetch_related("entries__project").order_by("week_start")[:12]

    data = []
    for dist in distributions:
        entries = []
        for entry in dist.entries.all():
            entries.append({
                "project_code": entry.project.code,
                "project_name": entry.project.name,
                "percentage": entry.percentage,
            })
        data.append({
            "week_start": dist.week_start.isoformat(),
            "entries": entries,
        })

    return JsonResponse({"distributions": data})
