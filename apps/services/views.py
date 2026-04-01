from collections import OrderedDict
from decimal import Decimal

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.template.response import TemplateResponse
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from apps.common.mixins import user_can_edit_pricing
from apps.services.forms import ProjectCategoryForm, ServiceTemplateForm
from apps.services.mixins import has_pricing_permission
from apps.services.models import (
    ProjectCategory,
    ProjectPhase,
    ServiceTemplate,
)


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


class ProjectCategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ProjectCategory
    template_name = "services/projectcategory_list.html"
    context_object_name = "categories"

    def get_queryset(self):
        return ProjectCategory.objects.order_by("code")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("services:category_create")
        return context


class ProjectCategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ProjectCategory
    form_class = ProjectCategoryForm
    template_name = "services/projectcategory_form.html"
    success_url = reverse_lazy("services:category_list")


class ProjectCategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ProjectCategory
    form_class = ProjectCategoryForm
    template_name = "services/projectcategory_form.html"
    success_url = reverse_lazy("services:category_list")


class ProjectCategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProjectCategory
    template_name = "services/projectcategory_confirm_delete.html"
    success_url = reverse_lazy("services:category_list")


class ProjectPhaseListView(LoginRequiredMixin, ListView):
    model = ProjectPhase
    template_name = "services/projectphase_list.html"
    context_object_name = "phases"


class ServiceTemplateListView(LoginRequiredMixin, ListView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_list.html"
    context_object_name = "service_templates"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("services:servicetemplate_create")
        return context


class ServiceTemplateDetailView(LoginRequiredMixin, DetailView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_detail.html"
    context_object_name = "service_template"


class ServiceTemplateCreateView(LoginRequiredMixin, CreateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")


class ServiceTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")


class ServiceTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_confirm_delete.html"
    success_url = reverse_lazy("services:servicetemplate_list")


# ---------------------------------------------------------------------------
# Pricing Dashboard
# ---------------------------------------------------------------------------


class PricingDashboardView(LoginRequiredMixin, ListView):
    model = ServiceTemplate
    template_name = "services/pricing_dashboard.html"
    context_object_name = "service_templates"

    def get_queryset(self):
        qs = ServiceTemplate.objects.select_related(
            "category", "phase", "operative_line",
        ).filter(is_active=True)
        line = self.request.GET.get("linea")
        if line:
            qs = qs.filter(operative_line__code=line)
        return qs.order_by("category__code", "code")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        all_templates = ServiceTemplate.objects.filter(is_active=True)

        context["total_services"] = all_templates.count()
        context["total_hours"] = all_templates.aggregate(
            h=Sum("estimated_hours"),
        )["h"] or 0
        context["visual_count"] = all_templates.filter(
            operative_line__code="VIS",
        ).count()
        context["design_count"] = all_templates.filter(
            operative_line__code="DV",
        ).count()
        context["current_line"] = self.request.GET.get("linea", "")

        # Group by category
        grouped = OrderedDict()
        for st in self.get_queryset():
            cat_name = str(st.category)
            if cat_name not in grouped:
                grouped[cat_name] = []
            grouped[cat_name].append(st)
        context["grouped_services"] = list(grouped.items())
        context["can_edit"] = user_can_edit_pricing(self.request.user)

        return context


class ServiceTemplateInlineEditView(LoginRequiredMixin, View):
    """HTMX inline edit for service template rows."""

    def get(self, request, pk):
        st = get_object_or_404(
            ServiceTemplate.objects.select_related("category", "phase"), pk=pk,
        )
        return TemplateResponse(
            request, "services/_pricing_row_edit.html", {"st": st},
        )

    def post(self, request, pk):
        st = get_object_or_404(
            ServiceTemplate.objects.select_related("category", "phase"), pk=pk,
        )

        if not has_pricing_permission(request.user):
            return HttpResponse("No tiene permisos", status=403)

        st.name = request.POST.get("name", st.name) or st.name
        try:
            st.base_unit_price = Decimal(request.POST.get("base_unit_price", ""))
        except Exception:
            pass
        try:
            st.estimated_hours = Decimal(request.POST.get("estimated_hours", ""))
        except Exception:
            pass
        try:
            st.target_margin_pct = Decimal(request.POST.get("target_margin_pct", ""))
        except Exception:
            pass
        st.is_active = "is_active" in request.POST
        st.save()

        return TemplateResponse(
            request, "services/_pricing_row_display.html", {"st": st},
        )


class ServiceTemplateInlineCancelView(LoginRequiredMixin, View):
    """Returns the display row, cancelling an edit."""

    def get(self, request, pk):
        st = get_object_or_404(
            ServiceTemplate.objects.select_related("category", "phase"), pk=pk,
        )
        return TemplateResponse(
            request, "services/_pricing_row_display.html", {"st": st},
        )
