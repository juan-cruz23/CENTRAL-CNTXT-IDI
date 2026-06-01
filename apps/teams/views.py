from datetime import date

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.forms import formset_factory, BaseFormSet
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.views.generic import TemplateView

from apps.accounts.models import User
from .models import WeeklyTeam, WeeklyTeamMember


# ---------------------------------------------------------------------------
# Permission helper
# ---------------------------------------------------------------------------
def _can_manage(user):
    if user.is_staff:
        return True
    try:
        return user.user_roles.filter(role__can_manage_teams=True).exists()
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Team list / management view
# ---------------------------------------------------------------------------
class TeamManagementView(LoginRequiredMixin, TemplateView):
    template_name = "teams/team_list.html"

    def dispatch(self, request, *args, **kwargs):
        if not _can_manage(request.user):
            return HttpResponseForbidden("No tienes permiso para gestionar equipos.")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = date.today()
        iso = today.isocalendar()
        ctx["current_week"] = iso[1]
        ctx["current_year"] = iso[0]
        ctx["teams"] = (
            WeeklyTeam.objects.filter(year=iso[0])
            .prefetch_related("members__user")
            .order_by("-week_number", "project_name")
        )
        ctx["active_users"] = User.objects.filter(is_active=True).order_by("first_name", "last_name")
        return ctx

    def post(self, request, *args, **kwargs):
        if not _can_manage(request.user):
            return HttpResponseForbidden()

        action = request.POST.get("action", "")

        # ── Crear equipo ───────────────────────────────────────────────────
        if action == "create":
            project_name = request.POST.get("project_name", "").strip()
            if not project_name:
                messages.error(request, "El nombre del proyecto es obligatorio.")
                return redirect("teams:list")

            today = date.today()
            iso = today.isocalendar()
            week_num = int(request.POST.get("week_number", iso[1]))
            year = iso[0]

            team = WeeklyTeam.objects.create(
                project_name=project_name,
                week_number=week_num,
                year=year,
                created_by=request.user,
            )

            # Miembros: llegan como listas paralelas user_id[] + occupation[]
            user_ids = request.POST.getlist("member_user_id")
            occupations = request.POST.getlist("member_occupation")

            for i, uid in enumerate(user_ids):
                if not uid:
                    continue
                occ = occupations[i].strip() if i < len(occupations) else ""
                try:
                    u = User.objects.get(pk=uid)
                    WeeklyTeamMember.objects.create(
                        team=team,
                        user=u,
                        occupation=occ or "—",
                        order=i,
                    )
                except User.DoesNotExist:
                    pass

            messages.success(request, f"Equipo «{project_name}» creado para la semana #{week_num}.")
            return redirect("teams:list")

        # ── Eliminar equipo ────────────────────────────────────────────────
        if action == "delete":
            team_id = request.POST.get("team_id")
            try:
                team = WeeklyTeam.objects.get(pk=team_id)
                name = team.project_name
                team.delete()
                messages.success(request, f"Equipo «{name}» eliminado.")
            except WeeklyTeam.DoesNotExist:
                messages.error(request, "El equipo no existe.")
            return redirect("teams:list")

        return redirect("teams:list")
