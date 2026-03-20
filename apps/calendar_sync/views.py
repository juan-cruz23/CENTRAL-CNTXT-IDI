from datetime import date, timedelta

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import ListView, TemplateView, View

from apps.calendar_sync.models import (
    CalendarEvent,
    GoogleCalendarConnection,
    ProjectColorMapping,
    ProjectKeywordMapping,
)
from apps.calendar_sync.services import get_unmatched_events, get_weekly_calendar_summary
from apps.projects.models import Project


class CalendarDashboardView(LoginRequiredMixin, TemplateView):
    """Main calendar sync dashboard."""

    template_name = "calendar_sync/dashboard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        # Connection status
        try:
            connection = user.calendar_connection
            context["is_connected"] = connection.is_active
            context["last_sync"] = connection.last_sync
        except GoogleCalendarConnection.DoesNotExist:
            context["is_connected"] = False
            context["last_sync"] = None

        # This week's events summary
        context["weekly_summary"] = get_weekly_calendar_summary(user, week_start)
        total_hours = sum(
            float(s["total_hours"] or 0) for s in context["weekly_summary"]
        )
        context["total_hours_week"] = round(total_hours, 1)

        # Unmatched events
        unmatched = get_unmatched_events(user)
        context["unmatched_events"] = unmatched[:10]
        context["unmatched_count"] = unmatched.count()

        # Active projects for manual assignment
        context["active_projects"] = Project.objects.filter(
            status="ACTIVE"
        ).order_by("code")

        # Color mappings
        context["color_mappings"] = ProjectColorMapping.objects.filter(
            user=user
        ).select_related("project")

        # Keyword mappings
        context["keyword_mappings"] = ProjectKeywordMapping.objects.select_related(
            "project"
        ).all()

        # Stats
        context["total_events"] = CalendarEvent.objects.filter(user=user).count()
        context["matched_events"] = CalendarEvent.objects.filter(
            user=user, project__isnull=False
        ).count()
        context["meeting_hours"] = CalendarEvent.objects.filter(
            user=user, is_meeting=True,
            start_time__date__gte=week_start,
        ).aggregate(h=Sum("duration_hours"))["h"] or 0

        return context


class CalendarEventListView(LoginRequiredMixin, ListView):
    """List all imported calendar events."""

    model = CalendarEvent
    template_name = "calendar_sync/event_list.html"
    context_object_name = "events"
    paginate_by = 30

    def get_queryset(self):
        qs = CalendarEvent.objects.filter(
            user=self.request.user
        ).select_related("project")

        match_filter = self.request.GET.get("match")
        if match_filter == "unmatched":
            qs = qs.filter(project__isnull=True)
        elif match_filter == "matched":
            qs = qs.filter(project__isnull=False)

        return qs


class AssignEventToProjectView(LoginRequiredMixin, View):
    """HTMX: Manually assign an event to a project."""

    def post(self, request, pk):
        event = get_object_or_404(CalendarEvent, pk=pk, user=request.user)
        project_id = request.POST.get("project_id")

        if project_id:
            project = get_object_or_404(Project, pk=project_id)
            event.project = project
            event.match_method = CalendarEvent.MatchMethod.MANUAL
            event.save()
            return JsonResponse({
                "status": "ok",
                "project_code": project.code,
                "project_name": project.name,
            })
        else:
            event.project = None
            event.match_method = CalendarEvent.MatchMethod.UNMATCHED
            event.save()
            return JsonResponse({"status": "cleared"})


class KeywordMappingCreateView(LoginRequiredMixin, View):
    """Create a new keyword mapping."""

    def post(self, request):
        keyword = request.POST.get("keyword", "").strip()
        project_id = request.POST.get("project_id")

        if not keyword or not project_id:
            messages.error(request, "Palabra clave y proyecto son requeridos.")
            return redirect("calendar_sync:dashboard")

        project = get_object_or_404(Project, pk=project_id)
        ProjectKeywordMapping.objects.get_or_create(
            project=project,
            keyword=keyword,
        )
        messages.success(request, f"Palabra clave '{keyword}' → {project.code} creada.")
        return redirect("calendar_sync:dashboard")


class KeywordMappingDeleteView(LoginRequiredMixin, View):
    """Delete a keyword mapping."""

    def post(self, request, pk):
        mapping = get_object_or_404(ProjectKeywordMapping, pk=pk)
        mapping.delete()
        messages.success(request, "Mapeo de palabra clave eliminado.")
        return redirect("calendar_sync:dashboard")


class CalendarWeeklySummaryAPI(LoginRequiredMixin, View):
    """API: Returns weekly hours by project for charts."""

    def get(self, request):
        user = request.user
        weeks_back = int(request.GET.get("weeks", 8))
        today = date.today()

        data = []
        for i in range(weeks_back - 1, -1, -1):
            week_start = today - timedelta(days=today.weekday()) - timedelta(weeks=i)
            summary = get_weekly_calendar_summary(user, week_start)
            data.append({
                "week_start": week_start.isoformat(),
                "week_label": week_start.strftime("%d %b"),
                "projects": summary,
                "total_hours": sum(float(s["total_hours"] or 0) for s in summary),
            })

        return JsonResponse({"weeks": data})
