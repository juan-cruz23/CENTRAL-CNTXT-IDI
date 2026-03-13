from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q, Sum, Value, DecimalField
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.projects.forms import (
    ClientForm,
    MilestoneForm,
    PrerequisiteForm,
    ProjectForm,
    ServiceInstanceCreateForm,
    ServiceInstanceForm,
)
from apps.projects.models import (
    Client,
    Milestone,
    Project,
    ProjectPhaseInstance,
    ProjectPrerequisite,
    ServiceInstance,
)
from apps.services.mixins import has_pricing_permission


# ---------------------------------------------------------------------------
# Project views
# ---------------------------------------------------------------------------
class ProjectListView(LoginRequiredMixin, ListView):
    """List projects with filtering by status and search by name/code."""

    model = Project
    template_name = "projects/project_list.html"
    context_object_name = "projects"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "client", "leader", "business_unit", "operative_line", "category",
        )
        # Filter by status
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        # Search by name or code
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = Project.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["create_url"] = reverse_lazy("projects:create")
        return context


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
                "client",
                "leader",
                "business_unit",
                "operative_line",
                "category",
            )
            .prefetch_related(
                "phase_instances__phase",
                "phase_instances__service_instances__assigned_professional",
                "phase_instances__service_instances__responsible_role",
                "milestones",
                "prerequisites",
            )
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object

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


class ProjectCreateView(LoginRequiredMixin, CreateView):
    """Create a new project."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

    def get_success_url(self):
        return reverse_lazy("projects:detail", kwargs={"pk": self.object.pk})


class ProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing project."""

    model = Project
    form_class = ProjectForm
    template_name = "projects/project_form.html"

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
# Client views
# ---------------------------------------------------------------------------
class ClientListView(LoginRequiredMixin, ListView):
    """List all clients with search support."""

    model = Client
    template_name = "projects/client_list.html"
    context_object_name = "clients"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(company__icontains=search)
            )
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["category_choices"] = Client.Category.choices
        context["current_category"] = self.request.GET.get("category", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["create_url"] = reverse_lazy("projects:client_create")
        return context


class ClientCreateView(LoginRequiredMixin, CreateView):
    """Create a new client."""

    model = Client
    form_class = ClientForm
    template_name = "projects/client_form.html"

    def get_success_url(self):
        return reverse_lazy("projects:client_list")
