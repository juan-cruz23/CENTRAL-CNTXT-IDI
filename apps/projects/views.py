from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView, View

from apps.projects.forms import ClientForm, ProjectForm, ServiceInstanceForm
from apps.projects.models import (
    Client,
    Project,
    ProjectPhaseInstance,
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
