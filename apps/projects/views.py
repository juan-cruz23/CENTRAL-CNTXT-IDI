from decimal import Decimal

from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.geography.models import Country, Municipality
from apps.projects.forms import (
    MilestoneForm,
    PrerequisiteForm,
    PrerequisiteTemplateForm,
    ProjectForm,
    ScheduleServiceForm,
    ScopeForm,
    ServiceInstanceCreateForm,
    ServiceInstanceForm,
)
from apps.projects.models import (
    ActionProgressLog,
    Milestone,
    PrerequisiteTemplate,
    Project,
    ProjectPhaseInstance,
    ProjectPrerequisite,
    ProjectScope,
    ServiceInstance,
    ServiceInstanceAction,
)
from apps.services.mixins import has_pricing_permission
from apps.terceros.models import ThirdParty


# ---------------------------------------------------------------------------
# Project views
# ---------------------------------------------------------------------------
class ProjectListView(LoginRequiredMixin, ListView):
    """List projects with filtering by status and search by name/code."""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 25

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["projects/partials/project_table_rows.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "third_party", "leader", "business_unit", "operative_line", "category",
        )
        user = self.request.user
        # Visibilidad: staff o can_access_all_projects ven todo; el resto solo sus proyectos
        if not user.is_staff:
            can_see_all = user.user_roles.filter(
                role__can_access_all_projects=True
            ).exists()
            if not can_see_all:
                qs = qs.filter(leader=user)
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        leader_id = self.request.GET.get("leader")
        if leader_id:
            qs = qs.filter(leader_id=leader_id)
        client_id = self.request.GET.get("client")
        if client_id:
            qs = qs.filter(third_party_id=client_id)
        code = self.request.GET.get("code")
        if code:
            qs = qs.filter(code__icontains=code)
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(name__icontains=search)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        User = get_user_model()
        context["status_choices"] = Project.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["current_leader"] = self.request.GET.get("leader", "")
        context["current_client"] = self.request.GET.get("client", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["search_code"] = self.request.GET.get("code", "")
        context["create_url"] = reverse_lazy("projects:create")
        context["leaders"] = User.objects.filter(
            led_projects__isnull=False
        ).distinct().order_by("first_name", "last_name")
        context["clients"] = ThirdParty.objects.filter(
            relationship_type=ThirdParty.RelationshipType.CLIENTE,
            projects__isnull=False,
        ).distinct().order_by("name")
        context["active_filters_count"] = sum([
            bool(self.request.GET.get("status")),
            bool(self.request.GET.get("leader")),
            bool(self.request.GET.get("client")),
            bool(self.request.GET.get("q")),
            bool(self.request.GET.get("code")),
        ])
        return context


@method_decorator(ensure_csrf_cookie, name="dispatch")
class ProjectDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a project with all related data prefetched."""

    model = Project
    template_name = "projects/project_detail.html"
    context_object_name = "project"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related(
                "third_party",
                "leader",
                "business_unit",
                "operative_line",
                "category",
            )
            .prefetch_related(
                "phase_instances__phase",
                "phase_instances__service_instances__assigned_professional",
                "phase_instances__service_instances__responsible_role",
                "service_instances__service_template__phase",
                "service_instances__assigned_professional",
                "service_instances__responsible_role",
                "milestones",
                "prerequisites",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

        # --- Cronograma: servicios agrupados por fase ---
        schedule_services = [
            si for si in project.service_instances.all()
            if si.phase_instance is None
        ]
        phase_groups_dict = {}
        for si in schedule_services:
            phase = si.service_template.phase if si.service_template else None
            sort_key = (phase.number if phase and hasattr(phase, 'number') else 999,
                        phase.pk if phase else 0)
            if sort_key not in phase_groups_dict:
                phase_groups_dict[sort_key] = {"phase": phase, "services": []}
            phase_groups_dict[sort_key]["services"].append(si)
        context["schedule_phase_groups"] = [
            v for _, v in sorted(phase_groups_dict.items())
        ]

        # Estadísticas de avance del cronograma
        total_ss = len(schedule_services)
        completed_ss  = sum(1 for s in schedule_services if s.progress_pct >= 100)
        in_progress_ss = sum(1 for s in schedule_services if 0 < s.progress_pct < 100)
        no_progress_ss = sum(1 for s in schedule_services if s.progress_pct == 0)
        overall_pct = round(
            sum(s.progress_pct for s in schedule_services) / total_ss, 1
        ) if total_ss else 0
        context["schedule_stats"] = {
            "total": total_ss,
            "completed": completed_ss,
            "in_progress": in_progress_ss,
            "no_progress": no_progress_ss,
            "overall_pct": overall_pct,
        }

        # --- Bloque 8: Financial summary for Info tab ---
        try:
            from apps.financials.models import PaymentMilestone

            payment_agg = PaymentMilestone.objects.filter(
                project=project
            ).aggregate(
                total_invoiced=Coalesce(
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
            context["financial_summary"] = {
                "total_value": project.total_value,
                "total_invoiced": payment_agg["total_invoiced"],
                "total_collected": payment_agg["total_collected"],
            }
            total_cost = ServiceInstance.objects.filter(
                project=project
            ).aggregate(
                total=Coalesce(
                    Sum("real_operative_cost"),
                    Value(Decimal("0")),
                    output_field=DecimalField(),
                ),
            )["total"]
            context["financial_summary"]["total_cost"] = total_cost
            collected = payment_agg["total_collected"]
            utility = collected - total_cost
            context["financial_summary"]["utility"] = utility
            if project.total_value and project.total_value > 0:
                context["financial_summary"]["margin_pct"] = (
                    utility / project.total_value * 100
                ).quantize(Decimal("0.01"))
            else:
                context["financial_summary"]["margin_pct"] = Decimal("0")
        except (ImportError, Exception):
            context["financial_summary"] = None

        # --- Bloque 8: Latest metric snapshot ---
        try:
            from apps.metrics.models import ProjectMetricSnapshot

            context["latest_snapshot"] = (
                ProjectMetricSnapshot.objects.filter(project=project)
                .order_by("-snapshot_date")
                .first()
            )
        except (ImportError, Exception):
            context["latest_snapshot"] = None

        # --- Bloque 6: Satisfaction data ---
        try:
            from apps.satisfaction.models import SatisfactionMeasurement

            context["satisfaction_measurements"] = (
                SatisfactionMeasurement.objects.filter(project=project)
                .select_related("milestone")
                .prefetch_related("survey")
            )
        except (ImportError, Exception):
            context["satisfaction_measurements"] = []

        # --- Fase actual ---
        try:
            phases = project.phase_instances.select_related("phase").order_by("phase__order", "phase__name")
            current_phase = None
            if phases.exists():
                # Buscar la primera en progreso (>0% y <100%)
                current_phase = phases.filter(
                    progress_pct__gt=0, progress_pct__lt=100
                ).first()
                if current_phase is None:
                    # Si ninguna en progreso, ver si todas completadas
                    if phases.filter(progress_pct__lt=100).exists():
                        current_phase = phases.filter(progress_pct=0).first()
                    else:
                        current_phase = "COMPLETED"
            context["current_phase"] = current_phase
        except Exception:
            context["current_phase"] = None

        # --- Documentos clave: cotización y contrato ---
        try:
            from apps.documents.models import ProjectDocument

            docs = ProjectDocument.objects.filter(project=project)
            context["doc_quotation"] = docs.filter(document_type="QUOTATION").order_by("-created_at").first()
            context["doc_contract"] = docs.filter(document_type="CONTRACT").order_by("-created_at").first()
        except (ImportError, Exception):
            context["doc_quotation"] = None
            context["doc_contract"] = None

        # --- Bloque 9: Active alerts ---
        try:
            from apps.notifications.models import Alert

            context["project_alerts"] = Alert.objects.filter(
                project=project,
                is_resolved=False,
            ).order_by("-created_at")[:10]
        except (ImportError, Exception):
            context["project_alerts"] = []

        try:
            from apps.capacity.models import CapacityAlert

            context["capacity_alerts"] = CapacityAlert.objects.filter(
                project=project,
                is_resolved=False,
            ).order_by("-created_at")[:10]
        except (ImportError, Exception):
            context["capacity_alerts"] = []

        return context


def _geo_context():
    return {
        "countries_list": Country.objects.filter(is_active=True).order_by("name"),
        "municipalities_list": Municipality.objects.filter(is_active=True).select_related("country").order_by("department", "name"),
    }


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a new project."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_geo_context()}

    def form_valid(self, form):
        # Generate next sequential code from existing numeric codes
        existing = (
            Project.objects.filter(code__regex=r"^\d+$")
            .values_list("code", flat=True)
        )
        max_code = max((int(c) for c in existing), default=237)
        form.instance.code = str(max_code + 1)
        response = super().form_valid(form)
        # Auto-load prerequisite templates for the selected category
        if self.object.category_id:
            _load_prerequisite_templates(self.object)
        return response

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing project."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def get_context_data(self, **kwargs):
        return {**super().get_context_data(**kwargs), **_geo_context()}

    def form_valid(self, form):
        # El campo code fue excluido del form; preservar el valor existente.
        form.instance.code = self.object.code
        old_category_id = self.get_object().category_id
        response = super().form_valid(form)
        # Si la categoría cambió o el proyecto no tenía prerrequisitos, cargar plantillas
        if self.object.category_id and (
            self.object.category_id != old_category_id
            or not self.object.prerequisites.exists()
        ):
            _load_prerequisite_templates(self.object)
        return response

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


# ---------------------------------------------------------------------------
# ServiceInstance views
# ---------------------------------------------------------------------------
class ServiceInstanceListView(LoginRequiredMixin, ListView):
    """List service instances for a specific project phase."""

    model = ServiceInstance
    template_name = "projects/service_instance_list.html"
    context_object_name = "service_instances"
    paginate_by = 50

    def get_queryset(self):
        self.project = get_object_or_404(Project, pk=self.kwargs["pk"])
        self.phase_instance = get_object_or_404(
            ProjectPhaseInstance,
            pk=self.kwargs["phase_pk"],
            project=self.project,
        )
        return (
            ServiceInstance.objects.filter(
                project=self.project,
                phase_instance=self.phase_instance,
            )
            .select_related(
                "assigned_professional",
                "responsible_role",
                "service_template",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.project
        context["phase_instance"] = self.phase_instance
        return context


class ServiceInstanceUpdateView(LoginRequiredMixin, UpdateView):
    """
    Update a service instance with HTMX inline editing support.
    When the request comes from HTMX (HX-Request header), return a partial
    template instead of the full page.
    """

    model = ServiceInstance
    form_class = ServiceInstanceForm
    template_name = "projects/service_instance_form.html"
    pk_url_kwarg = "si_pk"

    def get_queryset(self):
        return ServiceInstance.objects.filter(
            project_id=self.kwargs["pk"],
        ).select_related("project", "phase_instance")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["project"] = self.object.project
        return kwargs

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if not has_pricing_permission(self.request.user):
            for field_name in ("unit_price", "projected_hours", "quantity"):
                if field_name in form.fields:
                    form.fields[field_name].widget.attrs["readonly"] = True
                    form.fields[field_name].widget.attrs["class"] = (
                        form.fields[field_name].widget.attrs.get("class", "")
                        + " opacity-50 cursor-not-allowed"
                    )
        return form

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = self.object.project
        context["has_pricing_permission"] = has_pricing_permission(self.request.user)
        return context

    def get_success_url(self):
        return reverse_lazy(
            "projects:phase_services",
            kwargs={
                "pk": self.object.project_id,
                "phase_pk": self.object.phase_instance_id,
            },
        )

    def form_valid(self, form):
        response = super().form_valid(form)
        # If this is an HTMX request, return a partial template
        if self.request.headers.get("HX-Request"):
            return TemplateResponse(
                self.request,
                "projects/partials/service_instance_row.html",
                {"service_instance": self.object},
            )
        return response

    def form_invalid(self, form):
        # If this is an HTMX request, return the form partial with errors
        if self.request.headers.get("HX-Request"):
            return TemplateResponse(
                self.request,
                "projects/partials/service_instance_form_inline.html",
                {"form": form, "service_instance": self.object},
            )
        return super().form_invalid(form)


# ---------------------------------------------------------------------------
# ServiceInstance create / delete (Bloque 2)
# ---------------------------------------------------------------------------
class ServiceInstanceCreateView(LoginRequiredMixin, View):
    """HTMX endpoint: show form / create a new service instance."""

    def get(self, request, pk, phase_pk):
        project = get_object_or_404(Project, pk=pk)
        phase_instance = get_object_or_404(
            ProjectPhaseInstance, pk=phase_pk, project=project
        )
        form = ServiceInstanceCreateForm(project=project, phase_instance=phase_instance)
        return TemplateResponse(
            request,
            "projects/partials/service_create_form.html",
            {"form": form, "project": project, "phase_instance": phase_instance},
        )

    def post(self, request, pk, phase_pk):
        project = get_object_or_404(Project, pk=pk)
        phase_instance = get_object_or_404(
            ProjectPhaseInstance, pk=phase_pk, project=project
        )
        form = ServiceInstanceCreateForm(
            request.POST, project=project, phase_instance=phase_instance
        )
        if form.is_valid():
            si = form.save(commit=False)
            si.project = project
            si.phase_instance = phase_instance
            si.save()
            # Return the full service list to refresh the table
            service_instances = ServiceInstance.objects.filter(
                project=project, phase_instance=phase_instance,
            ).select_related("assigned_professional", "responsible_role", "service_template")
            return TemplateResponse(
                request,
                "projects/service_instance_list.html",
                {"service_instances": service_instances, "project": project, "phase_instance": phase_instance},
            )
        return TemplateResponse(
            request,
            "projects/partials/service_create_form.html",
            {"form": form, "project": project, "phase_instance": phase_instance},
        )


class ServiceInstanceDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete a service instance."""

    def delete(self, request, pk, si_pk):
        si = get_object_or_404(ServiceInstance, pk=si_pk, project_id=pk)
        si.delete()
        return HttpResponse("")


class ValidateAssignmentView(LoginRequiredMixin, View):
    """HTMX endpoint: check if assigned professional has allocation in project."""

    def get(self, request, pk):
        user_id = request.GET.get("assigned_professional")
        if not user_id:
            return HttpResponse("")

        from domain.capacity.services import CapacityService

        result = CapacityService.validate_assignment(int(user_id), pk)
        if result["has_allocation"]:
            return HttpResponse("")

        return TemplateResponse(
            request,
            "projects/partials/assignment_warning.html",
            {"warning": result["warning_message"], "project_pk": pk},
        )


# ---------------------------------------------------------------------------
# Prerequisite views
# ---------------------------------------------------------------------------
class PrerequisiteToggleView(LoginRequiredMixin, View):
    """HTMX endpoint: toggle prerequisite completion status."""

    def post(self, request, pk, prereq_pk):
        prereq = get_object_or_404(
            ProjectPrerequisite, pk=prereq_pk, project_id=pk
        )
        prereq.is_completed = not prereq.is_completed
        prereq.save()
        return TemplateResponse(
            request,
            "projects/partials/prerequisite_row.html",
            {"prereq": prereq, "project": prereq.project},
        )


class PrerequisiteCreateView(LoginRequiredMixin, View):
    """HTMX endpoint: show form / create a new prerequisite."""

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = PrerequisiteForm()
        return TemplateResponse(
            request,
            "projects/partials/prerequisite_form.html",
            {"form": form, "project": project},
        )

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = PrerequisiteForm(request.POST)
        if form.is_valid():
            prereq = form.save(commit=False)
            prereq.project = project
            prereq.save()
            return TemplateResponse(
                request,
                "projects/partials/prerequisite_row.html",
                {"prereq": prereq, "project": project},
            )
        return TemplateResponse(
            request,
            "projects/partials/prerequisite_form.html",
            {"form": form, "project": project},
        )


class PrerequisiteDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete a prerequisite."""

    def delete(self, request, pk, prereq_pk):
        prereq = get_object_or_404(
            ProjectPrerequisite, pk=prereq_pk, project_id=pk
        )
        prereq.delete()
        return HttpResponse("")


# ---------------------------------------------------------------------------
# Milestone views (Bloque 1)
# ---------------------------------------------------------------------------
class MilestoneCreateView(LoginRequiredMixin, View):
    """HTMX endpoint: show form / create a new milestone."""

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = MilestoneForm()
        return TemplateResponse(
            request,
            "projects/partials/milestone_form.html",
            {"form": form, "project": project},
        )

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.project = project
            milestone.save()
            return TemplateResponse(
                request,
                "projects/partials/milestone_row.html",
                {"milestone": milestone, "project": project},
            )
        return TemplateResponse(
            request,
            "projects/partials/milestone_form.html",
            {"form": form, "project": project},
        )


class MilestoneDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete a milestone."""

    def delete(self, request, pk, milestone_pk):
        milestone = get_object_or_404(Milestone, pk=milestone_pk, project_id=pk)
        milestone.delete()
        return HttpResponse("")


# ---------------------------------------------------------------------------
# Schedule service views (Cronograma — servicios con fecha planeada y fin calculado)
# ---------------------------------------------------------------------------

def _add_working_days(start_date, days):
    """
    Avanza `days` días hábiles desde `start_date`, excluyendo sábados,
    domingos y festivos colombianos de los próximos 12 meses.
    """
    from datetime import timedelta
    from apps.financials.models import ColombianHoliday

    days = int(days)
    if days <= 0:
        return start_date

    window_end = start_date + timedelta(days=max(days * 3, 365))
    holidays = set(
        ColombianHoliday.objects.filter(
            date__gte=start_date, date__lte=window_end,
        ).values_list("date", flat=True)
    )

    current = start_date
    remaining = days
    while remaining > 0:
        current += timedelta(days=1)
        if current.weekday() < 5 and current not in holidays:
            remaining -= 1
    return current


class CalcServiceEndDateView(LoginRequiredMixin, View):
    """
    HTMX: recibe service_template + projected_start_date,
    devuelve HTML con la fecha fin calculada.
    """

    def post(self, request, pk):
        from datetime import date as date_type
        from apps.services.models import ServiceTemplate
        from apps.accounts.models import WorkSchedule

        try:
            template_id = int(request.POST.get("service_template") or 0)
            start_str = request.POST.get("projected_start_date", "")
            start_date = date_type.fromisoformat(start_str)
        except (ValueError, TypeError):
            return HttpResponse('<span class="text-base-content/40 text-sm">— ingresa fecha de inicio —</span>')

        try:
            st = ServiceTemplate.objects.get(pk=template_id, is_active=True)
        except ServiceTemplate.DoesNotExist:
            return HttpResponse('<span class="text-base-content/40 text-sm">— selecciona un servicio —</span>')

        schedule = WorkSchedule.objects.filter(is_active=True).order_by("-weekly_hours").first()
        if not schedule:
            return HttpResponse('<span class="text-warning text-sm">Sin jornada laboral activa</span>')

        # Permite sobreescribir las horas (cuando el usuario edita acciones en el modal)
        from decimal import Decimal, InvalidOperation
        try:
            hours_override = Decimal(request.POST.get("total_hours") or "0")
        except InvalidOperation:
            hours_override = Decimal("0")
        hours = hours_override if hours_override > 0 else st.estimated_hours

        from apps.services.views import _working_days_needed
        days = _working_days_needed(hours, schedule.weekly_hours)
        end_date = _add_working_days(start_date, days)

        return HttpResponse(
            f'<span class="font-semibold">{end_date.strftime("%d/%m/%Y")}</span>'
            f'<span class="text-xs text-base-content/50 ml-2">({days} días hábiles · {hours}h)</span>'
        )


class ScheduleServiceCreateView(LoginRequiredMixin, View):
    """HTMX: carga el modal de agregar servicio (GET) / crea ServiceInstance + acciones (POST)."""

    def _suggested_start(self, project):
        last = (
            ServiceInstance.objects
            .filter(project=project, phase_instance=None, projected_end_date__isnull=False)
            .order_by("-projected_end_date")
            .values_list("projected_end_date", flat=True)
            .first()
        )
        return _add_working_days(last, 1) if last else None

    def get(self, request, pk):
        from apps.services.models import ServiceTemplate
        project = get_object_or_404(Project, pk=pk)
        service_templates = ServiceTemplate.objects.filter(is_active=True).select_related(
            "category", "phase", "responsible_role"
        ).order_by("code")
        return TemplateResponse(
            request,
            "projects/partials/schedule_service_modal.html",
            {
                "project": project,
                "service_templates": service_templates,
                "suggested_start": self._suggested_start(project),
            },
        )

    def post(self, request, pk):
        from apps.services.models import ServiceTemplate
        from apps.accounts.models import WorkSchedule, User as _User

        project = get_object_or_404(Project, pk=pk)

        # ── Campos de nivel servicio ──
        template_id = request.POST.get("service_template")
        start_raw   = request.POST.get("projected_start_date")
        prof_id     = request.POST.get("assigned_professional")

        if not template_id or not start_raw:
            return HttpResponse("Servicio y fecha de inicio son requeridos.", status=400)

        try:
            st = ServiceTemplate.objects.get(pk=int(template_id), is_active=True)
        except (ServiceTemplate.DoesNotExist, ValueError):
            return HttpResponse("Servicio no válido.", status=400)

        from datetime import date as _date
        try:
            start_date = _date.fromisoformat(start_raw)
        except ValueError:
            return HttpResponse("Fecha de inicio no válida.", status=400)

        # Horas totales: suma de acciones enviadas (o fallback a plantilla)
        act_total = int(request.POST.get("act-TOTAL") or 0)
        if act_total:
            total_hours = sum(
                Decimal(request.POST.get(f"act-{i}-hours") or "0")
                for i in range(act_total)
            )
        else:
            total_hours = st.estimated_hours

        schedule = WorkSchedule.objects.filter(is_active=True).order_by("-weekly_hours").first()
        from apps.services.views import _working_days_needed
        days = _working_days_needed(total_hours, schedule.weekly_hours) if schedule else 0
        end_date = _add_working_days(start_date, int(days)) if days else start_date

        professional = None
        if prof_id:
            try:
                professional = _User.objects.get(pk=int(prof_id), is_active=True)
            except (_User.DoesNotExist, ValueError):
                pass

        si = ServiceInstance.objects.create(
            project=project,
            phase_instance=None,
            service_template=st,
            code=st.code,
            name=st.name,
            unit_price=st.base_unit_price,
            projected_hours=total_hours,
            projected_days=days,
            projected_start_date=start_date,
            projected_end_date=end_date,
            responsible_role=st.responsible_role,
            assigned_professional=professional,
        )

        # ── Crear ServiceInstanceAction por cada acción ──
        for i in range(act_total):
            sa_id   = request.POST.get(f"act-{i}-service_activity")
            aname   = request.POST.get(f"act-{i}-name") or ""
            ahours  = Decimal(request.POST.get(f"act-{i}-hours") or "0")
            apro_id = request.POST.get(f"act-{i}-professional")
            arole_id = request.POST.get(f"act-{i}-role")

            if not aname.strip():
                continue

            sa_obj = None
            if sa_id:
                from apps.services.models import ServiceActivity
                try:
                    sa_obj = ServiceActivity.objects.get(pk=int(sa_id))
                except (ServiceActivity.DoesNotExist, ValueError):
                    pass

            apro = None
            if apro_id:
                try:
                    apro = _User.objects.get(pk=int(apro_id), is_active=True)
                except (_User.DoesNotExist, ValueError):
                    pass

            ServiceInstanceAction.objects.create(
                service_instance=si,
                service_activity=sa_obj,
                name=aname.strip(),
                order=i + 1,
                responsible_role_id=arole_id or None,
                assigned_professional=apro,
                estimated_hours=ahours,
            )

        response = TemplateResponse(
            request,
            "projects/partials/schedule_service_row.html",
            {"si": si, "project": project},
        )
        response["HX-Trigger"] = "closeAddServiceModal, scheduleChanged"
        return response


class ScheduleServiceTreeView(LoginRequiredMixin, View):
    """HTMX: dado un service_template, devuelve el árbol de acciones con inputs editables."""

    def get(self, request, pk):
        from apps.services.models import ServiceTemplate
        from apps.accounts.models import User

        template_id = request.GET.get("service_template")
        if not template_id:
            return HttpResponse("")

        try:
            st = ServiceTemplate.objects.get(pk=int(template_id), is_active=True)
        except (ServiceTemplate.DoesNotExist, ValueError):
            return HttpResponse("")

        # Árbol prefetched
        deliverables = list(
            st.deliverables
            .prefetch_related("key_activities__actions__responsible_role")
            .order_by("order", "name")
        )

        # Recoger todos los role_ids necesarios
        all_role_ids = set()
        if st.responsible_role_id:
            all_role_ids.add(st.responsible_role_id)
        for d in deliverables:
            for ka in d.key_activities.all():
                for act in ka.actions.all():
                    if act.responsible_role_id:
                        all_role_ids.add(act.responsible_role_id)

        # Cache: role_id → [User]
        role_users: dict[int, list] = {}
        for role_id in all_role_ids:
            role_users[role_id] = list(
                User.objects.filter(
                    user_roles__role_id=role_id,
                    is_active=True,
                ).distinct().order_by("first_name", "last_name")
            )

        # Construir lista plana de acciones con índice global
        actions_flat = []
        for d in deliverables:
            for ka in d.key_activities.all():
                for act in ka.actions.all():
                    actions_flat.append({
                        "idx": len(actions_flat),
                        "pk": act.pk,
                        "name": act.name,
                        "hours": act.estimated_hours,
                        "role_id": act.responsible_role_id,
                        "role_code": act.responsible_role.code if act.responsible_role else "",
                        "users": role_users.get(act.responsible_role_id, []),
                        "deliv_name": d.name,
                        "kact_name": ka.name,
                    })

        # Agrupar para el árbol visual
        tree = []
        for d in deliverables:
            kacts = []
            for ka in d.key_activities.all():
                acts = [a for a in actions_flat if a["deliv_name"] == d.name and a["kact_name"] == ka.name]
                kacts.append({"name": ka.name, "actions": acts})
            tree.append({"name": d.name, "unit": d.unit, "kacts": kacts})

        service_users = role_users.get(st.responsible_role_id, []) if st.responsible_role_id else []

        return TemplateResponse(
            request,
            "projects/partials/schedule_service_tree.html",
            {
                "st": st,
                "tree": tree,
                "actions_flat": actions_flat,
                "service_users": service_users,
                "act_total": len(actions_flat),
            },
        )


class ScheduleServiceDeleteView(LoginRequiredMixin, View):
    """HTMX: elimina un ServiceInstance del cronograma."""

    def delete(self, request, pk, si_pk):
        si = get_object_or_404(ServiceInstance, pk=si_pk, project_id=pk, phase_instance=None)
        si.delete()
        return HttpResponse("")


class ScheduleServiceActionsView(LoginRequiredMixin, View):
    """HTMX: retorna el árbol de acciones asignadas a una ServiceInstance."""

    def get(self, request, pk, si_pk):
        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)

        actions = list(
            si.action_assignments.select_related(
                "service_activity__key_activity__deliverable",
                "assigned_professional",
                "responsible_role",
            ).order_by("order")
        )

        # Agrupar: deliverable → key_activity → [acciones]
        tree = []
        seen_delivs = {}
        seen_kacts = {}
        for act in actions:
            sa = act.service_activity
            if sa and sa.key_activity and sa.key_activity.deliverable:
                d_name = sa.key_activity.deliverable.name
                d_unit = sa.key_activity.deliverable.unit
                ka_name = sa.key_activity.name
            else:
                d_name = "Sin entregable"
                d_unit = ""
                ka_name = "Sin actividad clave"

            if d_name not in seen_delivs:
                seen_delivs[d_name] = {"name": d_name, "unit": d_unit, "kacts": []}
                seen_kacts[d_name] = {}
                tree.append(seen_delivs[d_name])

            if ka_name not in seen_kacts[d_name]:
                kact_entry = {"name": ka_name, "actions": []}
                seen_kacts[d_name][ka_name] = kact_entry
                seen_delivs[d_name]["kacts"].append(kact_entry)

            seen_kacts[d_name][ka_name]["actions"].append(act)

        # Calcular progreso por actividad y por entregable
        for deliv in tree:
            for kact in deliv["kacts"]:
                acts = kact["actions"]
                total = len(acts)
                completed = sum(1 for a in acts if a.is_completed)
                kact["progress_pct"] = round(completed * 100 / total) if total else 0
                kact["completed"] = completed
                kact["total"] = total
            # Progreso del entregable = promedio de sus actividades
            kacts = deliv["kacts"]
            deliv["progress_pct"] = (
                round(sum(k["progress_pct"] for k in kacts) / len(kacts)) if kacts else 0
            )

        return TemplateResponse(
            request,
            "projects/partials/schedule_service_actions.html",
            {"si": si, "project": project, "tree": tree},
        )


class ScheduleServiceEditView(LoginRequiredMixin, View):
    """HTMX: carga el modal de edición de un servicio del cronograma (GET) / guarda cambios (POST)."""

    def _build_edit_tree(self, si):
        """Construye el árbol de acciones editable para una ServiceInstance."""
        from apps.accounts.models import User

        actions = list(
            si.action_assignments.select_related(
                "service_activity__key_activity__deliverable",
                "assigned_professional",
                "responsible_role",
            ).order_by("order")
        )

        # Recoger role_ids para filtrar usuarios
        role_ids = set()
        if si.responsible_role_id:
            role_ids.add(si.responsible_role_id)
        for act in actions:
            if act.responsible_role_id:
                role_ids.add(act.responsible_role_id)

        role_users = {}
        for role_id in role_ids:
            role_users[role_id] = list(
                User.objects.filter(
                    user_roles__role_id=role_id, is_active=True
                ).distinct().order_by("first_name", "last_name")
            )

        # Agrupar por entregable → actividad clave
        tree = []
        seen_delivs = {}
        seen_kacts = {}
        for idx, act in enumerate(actions):
            sa = act.service_activity
            if sa and sa.key_activity and sa.key_activity.deliverable:
                d_name = sa.key_activity.deliverable.name
                d_unit = sa.key_activity.deliverable.unit
                ka_name = sa.key_activity.name
            else:
                d_name = "Sin entregable"
                d_unit = ""
                ka_name = "Sin actividad clave"

            if d_name not in seen_delivs:
                seen_delivs[d_name] = {"name": d_name, "unit": d_unit, "kacts": []}
                seen_kacts[d_name] = {}
                tree.append(seen_delivs[d_name])

            if ka_name not in seen_kacts[d_name]:
                kact_entry = {"name": ka_name, "actions": []}
                seen_kacts[d_name][ka_name] = kact_entry
                seen_delivs[d_name]["kacts"].append(kact_entry)

            seen_kacts[d_name][ka_name]["actions"].append({
                "idx": idx,
                "obj": act,
                "users": role_users.get(act.responsible_role_id, []),
            })

        service_users = role_users.get(si.responsible_role_id, []) if si.responsible_role_id else []
        return tree, service_users, len(actions)

    def get(self, request, pk, si_pk):
        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)
        tree, service_users, act_total = self._build_edit_tree(si)
        return TemplateResponse(
            request,
            "projects/partials/schedule_service_edit_modal.html",
            {
                "project": project,
                "si": si,
                "tree": tree,
                "service_users": service_users,
                "act_total": act_total,
            },
        )

    def post(self, request, pk, si_pk):
        from apps.accounts.models import WorkSchedule, User as _User

        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)

        start_raw = request.POST.get("projected_start_date")
        prof_id   = request.POST.get("assigned_professional")
        act_total = int(request.POST.get("act-TOTAL") or 0)

        # Actualizar fecha inicio
        from datetime import date as _date
        if start_raw:
            try:
                start_date = _date.fromisoformat(start_raw)
                si.projected_start_date = start_date
            except ValueError:
                pass

        # Actualizar profesional responsable del servicio
        if prof_id:
            try:
                si.assigned_professional = _User.objects.get(pk=int(prof_id), is_active=True)
            except (_User.DoesNotExist, ValueError):
                si.assigned_professional = None
        else:
            si.assigned_professional = None

        # Recalcular horas totales y fecha fin a partir de las acciones editadas
        if act_total:
            total_hours = sum(
                Decimal(request.POST.get(f"act-{i}-hours") or "0")
                for i in range(act_total)
            )
        else:
            total_hours = si.projected_hours

        schedule = WorkSchedule.objects.filter(is_active=True).order_by("-weekly_hours").first()
        from apps.services.views import _working_days_needed
        days = _working_days_needed(total_hours, schedule.weekly_hours) if schedule else 0
        end_date = _add_working_days(si.projected_start_date, int(days)) if days and si.projected_start_date else si.projected_start_date

        si.projected_hours = total_hours
        si.projected_days  = days
        si.projected_end_date = end_date
        si.save(update_fields=[
            "projected_start_date", "projected_end_date",
            "projected_hours", "projected_days", "assigned_professional",
        ])

        # Actualizar ServiceInstanceAction (horas + profesional)
        actions = list(si.action_assignments.order_by("order"))
        for i, act in enumerate(actions):
            new_hours = Decimal(request.POST.get(f"act-{i}-hours") or "0")
            pro_id    = request.POST.get(f"act-{i}-professional")
            act.estimated_hours = new_hours
            if pro_id:
                try:
                    act.assigned_professional = _User.objects.get(pk=int(pro_id), is_active=True)
                except (_User.DoesNotExist, ValueError):
                    act.assigned_professional = None
            else:
                act.assigned_professional = None
            act.save(update_fields=["estimated_hours", "assigned_professional"])

        response = HttpResponse("")
        response["HX-Trigger"] = "scheduleChanged"
        return response


class ActionToggleView(LoginRequiredMixin, View):
    """HTMX: marca/desmarca una acción como completada y guarda horas reales.
    Retorna la fila de la acción actualizada y un evento actionToggled para
    que el servicio recalcule su progreso.
    """

    def post(self, request, pk, si_pk, action_pk):
        from django.utils import timezone

        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)
        action = get_object_or_404(ServiceInstanceAction, pk=action_pk, service_instance=si)

        is_completed = request.POST.get("is_completed") == "1"
        actual_hours_raw = request.POST.get("actual_hours", "").strip()
        try:
            actual_hours = Decimal(actual_hours_raw) if actual_hours_raw else action.actual_hours
        except Exception:
            actual_hours = action.actual_hours

        action.is_completed = is_completed
        action.actual_hours = actual_hours
        action.completed_at = timezone.now() if is_completed else None
        action.save(update_fields=["is_completed", "actual_hours", "completed_at"])

        # Recalcular progress_pct y actual_hours del servicio basado en acciones
        all_actions = list(si.action_assignments.all())
        total = len(all_actions)
        completed = sum(1 for a in all_actions if a.is_completed)
        total_actual = sum(a.actual_hours for a in all_actions)
        si.progress_pct = Decimal(completed * 100 / total) if total else Decimal(0)
        si.actual_hours = total_actual
        si.save(update_fields=["progress_pct", "actual_hours", "operative_deviation_pct"])

        response = TemplateResponse(
            request,
            "projects/partials/action_row.html",
            {"action": action, "project": project, "si": si},
        )
        response["HX-Trigger"] = "actionToggled"
        return response


class ActionProgressLogView(LoginRequiredMixin, View):
    """HTMX: GET → modal para registrar avance; POST → guarda y marca acción completada."""

    def get(self, request, pk, si_pk, action_pk):
        from apps.accounts.models import User
        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)
        action = get_object_or_404(ServiceInstanceAction, pk=action_pk, service_instance=si)
        users = User.objects.filter(is_active=True).order_by("first_name", "last_name")
        return TemplateResponse(
            request,
            "projects/partials/action_progress_modal.html",
            {"action": action, "si": si, "project": project, "users": users},
        )

    def post(self, request, pk, si_pk, action_pk):
        from django.utils import timezone
        from apps.accounts.models import User

        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)
        action = get_object_or_404(ServiceInstanceAction, pk=action_pk, service_instance=si)

        description = request.POST.get("description", "").strip()
        folder_link = request.POST.get("folder_link", "").strip() or None
        start_dt_raw = request.POST.get("start_datetime", "").strip()
        end_dt_raw = request.POST.get("end_datetime", "").strip()
        executed_by_id = request.POST.get("executed_by", "").strip()
        attachment = request.FILES.get("attachment")

        if not start_dt_raw or not end_dt_raw or not executed_by_id:
            return HttpResponse("Faltan campos requeridos.", status=400)

        from datetime import datetime
        try:
            start_dt = datetime.fromisoformat(start_dt_raw)
            end_dt = datetime.fromisoformat(end_dt_raw)
        except ValueError:
            return HttpResponse("Formato de fecha/hora inválido.", status=400)

        if end_dt <= start_dt:
            return HttpResponse("La hora fin debe ser posterior a la hora inicio.", status=400)

        executed_by = get_object_or_404(User, pk=executed_by_id)

        log = ActionProgressLog(
            action=action,
            description=description,
            folder_link=folder_link,
            start_datetime=start_dt,
            end_datetime=end_dt,
            executed_by=executed_by,
        )
        if attachment:
            log.attachment = attachment
        log.save()

        # Crear ProjectDocument automáticamente si hay adjunto o link
        from apps.documents.models import ProjectDocument
        doc_name = f"{action.name} — {si.code}"
        if attachment:
            ProjectDocument.objects.create(
                project=project,
                service_instance=si,
                document_type=ProjectDocument.DocumentType.DELIVERABLE,
                audience=ProjectDocument.Audience.INTERNAL,
                name=doc_name,
                file=log.attachment,
                notes=description,
            )
        if folder_link:
            ProjectDocument.objects.create(
                project=project,
                service_instance=si,
                document_type=ProjectDocument.DocumentType.DELIVERABLE,
                audience=ProjectDocument.Audience.INTERNAL,
                name=doc_name,
                access_link=folder_link,
                notes=description,
            )

        # Marcar acción como completada
        action.is_completed = True
        action.completed_at = timezone.now()

        # Recalcular horas reales sumando todos los registros
        total_hours = sum(
            log_entry.hours for log_entry in action.progress_logs.all()
        )
        action.actual_hours = Decimal(str(total_hours))
        action.save(update_fields=["is_completed", "completed_at", "actual_hours"])

        # Recalcular progreso del servicio
        all_actions = list(si.action_assignments.all())
        total = len(all_actions)
        completed = sum(1 for a in all_actions if a.is_completed)
        total_actual = sum(a.actual_hours for a in all_actions)
        si.progress_pct = Decimal(completed * 100 / total) if total else Decimal(0)
        si.actual_hours = total_actual
        if si.projected_hours and si.actual_hours:
            si.operative_deviation_pct = round(
                (si.actual_hours - si.projected_hours) / si.projected_hours * 100, 2
            )
        else:
            si.operative_deviation_pct = Decimal(0)
        si.save(update_fields=["progress_pct", "actual_hours", "operative_deviation_pct"])

        response = TemplateResponse(
            request,
            "projects/partials/action_row.html",
            {"action": action, "project": project, "si": si},
        )
        response["HX-Trigger"] = "actionToggled"
        return response


class ActionProgressHistoryView(LoginRequiredMixin, View):
    """HTMX: modal con el historial de registros de avance de una acción."""

    def get(self, request, pk, si_pk, action_pk):
        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)
        action = get_object_or_404(ServiceInstanceAction, pk=action_pk, service_instance=si)
        logs = action.progress_logs.select_related("executed_by").order_by("start_datetime")
        return TemplateResponse(
            request,
            "projects/partials/action_progress_history_modal.html",
            {"action": action, "si": si, "project": project, "logs": logs},
        )


class ServiceApprovalView(LoginRequiredMixin, View):
    """HTMX: GET → modal de aprobación (solo líder); POST → aprueba o rechaza."""

    def _check_leader(self, request, project):
        return request.user == project.leader

    def get(self, request, pk, si_pk):
        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)

        # Construir árbol de progreso para revisión
        actions = list(
            si.action_assignments.select_related(
                "service_activity__key_activity__deliverable",
                "assigned_professional",
            ).order_by("order")
        )
        tree = []
        seen_delivs = {}
        seen_kacts = {}
        for act in actions:
            sa = act.service_activity
            if sa and sa.key_activity and sa.key_activity.deliverable:
                d_name = sa.key_activity.deliverable.name
                ka_name = sa.key_activity.name
            else:
                d_name = "Sin entregable"
                ka_name = "Sin actividad clave"
            if d_name not in seen_delivs:
                seen_delivs[d_name] = {"name": d_name, "kacts": []}
                seen_kacts[d_name] = {}
                tree.append(seen_delivs[d_name])
            if ka_name not in seen_kacts[d_name]:
                kact_entry = {"name": ka_name, "actions": []}
                seen_kacts[d_name][ka_name] = kact_entry
                seen_delivs[d_name]["kacts"].append(kact_entry)
            seen_kacts[d_name][ka_name]["actions"].append(act)

        for deliv in tree:
            for kact in deliv["kacts"]:
                acts = kact["actions"]
                total = len(acts)
                completed = sum(1 for a in acts if a.is_completed)
                kact["progress_pct"] = round(completed * 100 / total) if total else 0
                kact["completed"] = completed
                kact["total"] = total
            kacts = deliv["kacts"]
            deliv["progress_pct"] = (
                round(sum(k["progress_pct"] for k in kacts) / len(kacts)) if kacts else 0
            )

        is_leader = self._check_leader(request, project)
        return TemplateResponse(
            request,
            "projects/partials/service_approval_modal.html",
            {"si": si, "project": project, "tree": tree, "is_leader": is_leader},
        )

    def post(self, request, pk, si_pk):
        from django.utils import timezone
        project = get_object_or_404(Project, pk=pk)
        si = get_object_or_404(ServiceInstance, pk=si_pk, project=project)

        if not self._check_leader(request, project):
            return HttpResponse("Solo el líder del proyecto puede aprobar servicios.", status=403)

        decision = request.POST.get("decision")
        notes = request.POST.get("approval_notes", "").strip()

        if decision == "approve":
            si.approval_status = ServiceInstance.ApprovalStatus.APPROVED
            si.is_checked = True
            si.progress_pct = Decimal("100.00")
        elif decision == "reject":
            si.approval_status = ServiceInstance.ApprovalStatus.REJECTED
            si.is_checked = False
        else:
            return HttpResponse("Decisión inválida.", status=400)

        si.approval_notes = notes
        si.approved_by = request.user
        si.approved_at = timezone.now()
        si.save(update_fields=["approval_status", "approval_notes", "approved_by", "approved_at", "is_checked", "progress_pct"])

        response = TemplateResponse(
            request,
            "projects/partials/service_approval_badge.html",
            {"si": si, "project": project},
        )
        response["HX-Trigger"] = "scheduleChanged"
        return response


class ScheduleTableView(LoginRequiredMixin, View):
    """HTMX: retorna el contenido del tbody del cronograma (servicios agrupados por fase)."""

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        schedule_services = list(
            ServiceInstance.objects.filter(project=project, phase_instance=None)
            .select_related(
                "service_template__phase",
                "assigned_professional",
                "responsible_role",
            )
            .order_by("service_template__phase__number", "projected_start_date")
        )
        phase_groups_dict = {}
        for si in schedule_services:
            phase = si.service_template.phase if si.service_template else None
            sort_key = (
                phase.number if phase and hasattr(phase, "number") else 999,
                phase.pk if phase else 0,
            )
            if sort_key not in phase_groups_dict:
                phase_groups_dict[sort_key] = {"phase": phase, "services": []}
            phase_groups_dict[sort_key]["services"].append(si)
        phase_groups = [v for _, v in sorted(phase_groups_dict.items())]

        return TemplateResponse(
            request,
            "projects/partials/schedule_table_body.html",
            {"phase_groups": phase_groups, "project": project},
        )


class ScheduleServiceResponsiblesView(LoginRequiredMixin, View):
    """
    HTMX: dado un service_template, devuelve un <select> con los usuarios
    que tienen el rol responsable asignado. Si solo hay uno, lo preselecciona.
    """

    def get(self, request, pk):
        from apps.accounts.models import User, UserRole
        from apps.services.models import ServiceTemplate

        template_id = request.GET.get("service_template")
        users = []
        auto_select = None

        if template_id:
            try:
                st = ServiceTemplate.objects.select_related("responsible_role").get(
                    pk=template_id, is_active=True
                )
                if st.responsible_role:
                    users = list(
                        User.objects.filter(
                            user_roles__role=st.responsible_role,
                            is_active=True,
                        ).distinct().order_by("first_name", "last_name")
                    )
                    if len(users) == 1:
                        auto_select = users[0].pk
            except ServiceTemplate.DoesNotExist:
                pass

        options_html = '<option value="">— Sin asignar —</option>'
        for u in users:
            selected = 'selected' if u.pk == auto_select else ''
            options_html += f'<option value="{u.pk}" {selected}>{u.get_full_name()}</option>'

        html = f'<select name="assigned_professional" id="id_assigned_professional" class="select select-bordered select-sm w-full">{options_html}</select>'
        return HttpResponse(html)


# ---------------------------------------------------------------------------
# Scope views
# ---------------------------------------------------------------------------
class ScopeCreateView(LoginRequiredMixin, View):
    """HTMX endpoint: show form / create a new scope."""

    def get(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ScopeForm()
        return TemplateResponse(
            request,
            "projects/partials/scope_form.html",
            {"form": form, "project": project},
        )

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        form = ScopeForm(request.POST)
        if form.is_valid():
            scope = form.save(commit=False)
            scope.project = project
            scope.save()
            return TemplateResponse(
                request,
                "projects/partials/scope_row.html",
                {"scope": scope, "project": project},
            )
        return TemplateResponse(
            request,
            "projects/partials/scope_form.html",
            {"form": form, "project": project},
        )


class ScopeEditView(LoginRequiredMixin, View):
    """HTMX endpoint: show edit form / save a scope."""

    def get(self, request, pk, scope_pk):
        project = get_object_or_404(Project, pk=pk)
        scope = get_object_or_404(ProjectScope, pk=scope_pk, project_id=pk)
        return TemplateResponse(request, "projects/partials/scope_edit_form.html",
                                {"scope": scope, "project": project})

    def post(self, request, pk, scope_pk):
        project = get_object_or_404(Project, pk=pk)
        scope = get_object_or_404(ProjectScope, pk=scope_pk, project_id=pk)
        form = ScopeForm(request.POST, instance=scope)
        if form.is_valid():
            form.save()
            return TemplateResponse(request, "projects/partials/scope_row.html",
                                    {"scope": scope, "project": project})
        return TemplateResponse(request, "projects/partials/scope_edit_form.html",
                                {"scope": scope, "project": project, "form": form})


class ScopeCancelEditView(LoginRequiredMixin, View):
    """HTMX endpoint: cancel edit, return original row."""

    def get(self, request, pk, scope_pk):
        project = get_object_or_404(Project, pk=pk)
        scope = get_object_or_404(ProjectScope, pk=scope_pk, project_id=pk)
        return TemplateResponse(request, "projects/partials/scope_row.html",
                                {"scope": scope, "project": project})


class ScopeDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete a scope."""

    def delete(self, request, pk, scope_pk):
        scope = get_object_or_404(ProjectScope, pk=scope_pk, project_id=pk)
        scope.delete()
        return HttpResponse("")


# ---------------------------------------------------------------------------
# Prerequisite template helpers
# ---------------------------------------------------------------------------
def _load_prerequisite_templates(project):
    """Create ProjectPrerequisite instances from templates for the project's category."""
    templates = PrerequisiteTemplate.objects.filter(
        project_category=project.category
    )
    for tpl in templates:
        ProjectPrerequisite.objects.get_or_create(
            project=project,
            category=tpl.category,
            prerequisite_type=tpl.prerequisite_type,
            defaults={"name": tpl.name, "weight_pct": tpl.weight_pct},
        )


# ---------------------------------------------------------------------------
# Prerequisite load-template HTMX endpoint
# ---------------------------------------------------------------------------
class PrerequisiteLoadTemplateView(LoginRequiredMixin, View):
    """HTMX endpoint: load prerequisite templates for the project's category."""

    def post(self, request, pk):
        project = get_object_or_404(Project, pk=pk)
        if not project.category_id:
            return HttpResponse(
                '<div class="alert alert-warning text-sm">El proyecto no tiene categoría asignada.</div>'
            )
        created_count = 0
        templates = PrerequisiteTemplate.objects.filter(project_category=project.category)
        if not templates.exists():
            return HttpResponse(
                '<div class="alert alert-info text-sm">No hay plantillas configuradas para esta categoría.</div>'
            )
        for tpl in templates:
            _, created = ProjectPrerequisite.objects.get_or_create(
                project=project,
                category=tpl.category,
                prerequisite_type=tpl.prerequisite_type,
                defaults={"name": tpl.name, "weight_pct": tpl.weight_pct},
            )
            if created:
                created_count += 1
        prereqs = project.prerequisites.all()
        return TemplateResponse(
            request,
            "projects/partials/prereqs_tbody.html",
            {"prereqs": prereqs, "project": project, "loaded_count": created_count},
        )


# ---------------------------------------------------------------------------
# PrerequisiteTemplate CRUD (Maestros)
# ---------------------------------------------------------------------------
class PrerequisiteTemplateListView(LoginRequiredMixin, ListView):
    model = PrerequisiteTemplate
    template_name = "projects/prerequisite_template_list.html"
    context_object_name = "templates"

    def get_queryset(self):
        return super().get_queryset().select_related("project_category")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("projects:prereq_template_create")
        return context


class PrerequisiteTemplateCreateView(LoginRequiredMixin, CreateView):
    model = PrerequisiteTemplate
    form_class = PrerequisiteTemplateForm
    template_name = "projects/prerequisite_template_form.html"

    def get_success_url(self):
        return reverse_lazy("projects:prereq_template_list")


class PrerequisiteTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = PrerequisiteTemplate
    form_class = PrerequisiteTemplateForm
    template_name = "projects/prerequisite_template_form.html"

    def get_success_url(self):
        return reverse_lazy("projects:prereq_template_list")


class PrerequisiteTemplateDeleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        tpl = get_object_or_404(PrerequisiteTemplate, pk=pk)
        tpl.delete()
        return HttpResponse(status=204, headers={"HX-Redirect": reverse_lazy("projects:prereq_template_list")})
