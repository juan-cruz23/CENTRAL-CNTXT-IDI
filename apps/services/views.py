from collections import OrderedDict
from datetime import date, timedelta
from decimal import Decimal
from math import ceil

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
from apps.services.forms import DeliverableForm, HardwareForm, KeyActivityForm, ProjectCategoryForm, ProjectPhaseForm, ServiceSubCategoryForm, ServiceTemplateForm, SoftwareForm
from apps.services.mixins import has_pricing_permission
from apps.services.models import (
    Deliverable,
    Hardware,
    KeyActivity,
    ProjectCategory,
    ProjectPhase,
    ServiceSubCategory,
    ServiceTemplate,
    Software,
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


class HardwareListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Hardware
    template_name = "services/hardware_list.html"
    context_object_name = "hardware_list"


class HardwareCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Hardware
    form_class = HardwareForm
    template_name = "services/hardware_form.html"
    success_url = reverse_lazy("services:hardware_list")


class HardwareUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Hardware
    form_class = HardwareForm
    template_name = "services/hardware_form.html"
    success_url = reverse_lazy("services:hardware_list")


class HardwareDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Hardware
    template_name = "services/hardware_confirm_delete.html"
    success_url = reverse_lazy("services:hardware_list")


class SoftwareListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Software
    template_name = "services/software_list.html"
    context_object_name = "software_list"


class SoftwareCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Software
    form_class = SoftwareForm
    template_name = "services/software_form.html"
    success_url = reverse_lazy("services:software_list")


class SoftwareUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Software
    form_class = SoftwareForm
    template_name = "services/software_form.html"
    success_url = reverse_lazy("services:software_list")


class SoftwareDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Software
    template_name = "services/software_confirm_delete.html"
    success_url = reverse_lazy("services:software_list")


class ServiceSubCategoryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ServiceSubCategory
    template_name = "services/servicesubcategory_list.html"
    context_object_name = "subcategories"

    def get_queryset(self):
        return ServiceSubCategory.objects.order_by("code")


class ServiceSubCategoryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ServiceSubCategory
    form_class = ServiceSubCategoryForm
    template_name = "services/servicesubcategory_form.html"
    success_url = reverse_lazy("services:subcategory_list")


class ServiceSubCategoryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ServiceSubCategory
    form_class = ServiceSubCategoryForm
    template_name = "services/servicesubcategory_form.html"
    success_url = reverse_lazy("services:subcategory_list")


class ServiceSubCategoryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ServiceSubCategory
    template_name = "services/servicesubcategory_confirm_delete.html"
    success_url = reverse_lazy("services:subcategory_list")


class ProjectPhaseListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ProjectPhase
    template_name = "services/projectphase_list.html"
    context_object_name = "phases"


class ProjectPhaseCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ProjectPhase
    form_class = ProjectPhaseForm
    template_name = "services/projectphase_form.html"
    success_url = reverse_lazy("services:phase_list")


class ProjectPhaseUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ProjectPhase
    form_class = ProjectPhaseForm
    template_name = "services/projectphase_form.html"
    success_url = reverse_lazy("services:phase_list")


class ProjectPhaseDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ProjectPhase
    template_name = "services/projectphase_confirm_delete.html"
    success_url = reverse_lazy("services:phase_list")


class DeliverableListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Deliverable
    template_name = "services/deliverable_list.html"
    context_object_name = "deliverables"

    def get_queryset(self):
        return Deliverable.objects.select_related("service_template", "service_template__category").order_by(
            "service_template__code", "order", "name"
        )


class DeliverableCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Deliverable
    form_class = DeliverableForm
    template_name = "services/deliverable_form.html"
    success_url = reverse_lazy("services:deliverable_list")


class DeliverableUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Deliverable
    form_class = DeliverableForm
    template_name = "services/deliverable_form.html"
    success_url = reverse_lazy("services:deliverable_list")


class DeliverableDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Deliverable
    template_name = "services/deliverable_confirm_delete.html"
    success_url = reverse_lazy("services:deliverable_list")


class KeyActivityListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = KeyActivity
    template_name = "services/keyactivity_list.html"
    context_object_name = "activities"

    def get_queryset(self):
        return KeyActivity.objects.select_related(
            "deliverable__service_template"
        ).order_by("deliverable__service_template__code", "deliverable__name", "order", "name")


class KeyActivityCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = KeyActivity
    form_class = KeyActivityForm
    template_name = "services/keyactivity_form.html"
    success_url = reverse_lazy("services:keyactivity_list")


class KeyActivityUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = KeyActivity
    form_class = KeyActivityForm
    template_name = "services/keyactivity_form.html"
    success_url = reverse_lazy("services:keyactivity_list")


class KeyActivityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = KeyActivity
    template_name = "services/keyactivity_confirm_delete.html"
    success_url = reverse_lazy("services:keyactivity_list")


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

    def get_context_data(self, **kwargs):
        from apps.accounts.models import WorkSchedule
        context = super().get_context_data(**kwargs)
        st = self.object
        schedule = WorkSchedule.objects.filter(is_active=True).order_by("-weekly_hours").first()
        if schedule and st.estimated_hours:
            days = _working_days_needed(st.estimated_hours, schedule.weekly_hours)
            if Decimal(days) != st.estimated_days:
                st.estimated_days = Decimal(days)
                st.save(update_fields=["estimated_days"])
        context["default_schedule"] = schedule
        return context


def _role_rates_json():
    """Returns a JSON-serializable dict {role_pk: default_hourly_rate} for all active roles."""
    import json
    from apps.accounts.models import Role
    rates = {str(r.pk): str(r.default_hourly_rate) for r in Role.objects.filter(is_active=True)}
    return json.dumps(rates)


class ServiceTemplateCreateView(LoginRequiredMixin, CreateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_rates_json"] = _role_rates_json()
        return context


class ServiceTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_rates_json"] = _role_rates_json()
        return context


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


def _working_days_needed(estimated_hours, weekly_hours):
    """
    Calcula cuántos días hábiles (lun-vie, sin festivos colombianos) se
    necesitan para cubrir `estimated_hours` con una jornada de `weekly_hours`
    horas semanales.

    Pasos:
      1. Días hábiles puros = ceil(horas / (jornada_semanal / 5))
      2. Festivos que caen en día hábil en los próximos 12 meses → tasa mensual
      3. Se añaden los festivos proporcionales al período estimado
    """
    from apps.financials.models import ColombianHoliday

    if not weekly_hours or not estimated_hours or weekly_hours <= 0:
        return 0

    hours_per_day = float(weekly_hours) / 5
    raw_days = ceil(float(estimated_hours) / hours_per_day)

    # Festivos en ventana de 12 meses que caigan en día hábil (lun-vie)
    today = date.today()
    window_end = today + timedelta(days=365)
    weekday_holidays = ColombianHoliday.objects.filter(
        date__gte=today,
        date__lte=window_end,
        date__week_day__in=[2, 3, 4, 5, 6],  # Django: 1=dom … 2=lun … 6=vie … 7=sáb
    ).count()

    # Proporción de festivos en el período estimado
    # 260 ≈ días hábiles por año (52 semanas × 5)
    holidays_in_period = round(weekday_holidays * raw_days / 260)
    return raw_days + holidays_in_period


class CalcHoursDaysView(LoginRequiredMixin, View):
    """
    HTMX: convierte horas ↔ días en el form de ServiceTemplate.
    Si recibe estimated_hours → devuelve input de estimated_days calculado.
    Si recibe estimated_days → devuelve input de estimated_hours calculado.
    Usa el primer WorkSchedule activo (mayor jornada).
    """

    def post(self, request):
        from apps.accounts.models import WorkSchedule
        schedule = WorkSchedule.objects.filter(is_active=True).order_by("-weekly_hours").first()
        if not schedule:
            return HttpResponse("")

        hours_per_day = float(schedule.weekly_hours) / 5

        raw_hours = request.POST.get("estimated_hours")
        raw_days = request.POST.get("estimated_days")

        if raw_hours not in (None, ""):
            try:
                hours = float(raw_hours)
                days = _working_days_needed(hours, schedule.weekly_hours)
            except (ValueError, TypeError):
                days = 0
            return HttpResponse(
                f'<input type="number" name="estimated_days" id="id_estimated_days" '
                f'value="{days}" step="0.5" class="form-control" '
                f'hx-post="/servicios/calcular-horas-dias/" hx-trigger="change" '
                f'hx-include="[name=\'estimated_days\']" hx-target="#id_estimated_hours" hx-swap="outerHTML">'
            )
        elif raw_days not in (None, ""):
            try:
                days = float(raw_days)
                hours = round(days * hours_per_day, 2)
            except (ValueError, TypeError):
                hours = 0
            return HttpResponse(
                f'<input type="number" name="estimated_hours" id="id_estimated_hours" '
                f'value="{hours}" step="0.1" class="form-control" '
                f'hx-post="/servicios/calcular-horas-dias/" hx-trigger="change" '
                f'hx-include="[name=\'estimated_hours\']" hx-target="#id_estimated_days" hx-swap="outerHTML">'
            )
        return HttpResponse("")


class CalcPricingView(LoginRequiredMixin, View):
    """
    HTMX: recibe los campos de pricing del form, devuelve el desglose calculado.
    No requiere pk — funciona en create y update.
    """

    def post(self, request):
        def dec(key, default="0"):
            try:
                return Decimal(request.POST.get(key, default) or default)
            except Exception:
                return Decimal("0")

        from apps.services.models import ServiceTemplate as ST
        st = ST()
        st.estimated_hours = dec("estimated_hours")
        st.hourly_rate = dec("hourly_rate")
        st.hardware_cost_per_hour = dec("hardware_cost_per_hour")
        st.software_cost_per_hour = dec("software_cost_per_hour")
        st.consumables_per_hour = dec("consumables_per_hour")
        st.subcontracts = dec("subcontracts")
        st.contingency_pct = dec("contingency_pct", "15")
        st.utility_pct = dec("utility_pct", "20")
        st.negotiation_pct = dec("negotiation_pct", "5")
        return TemplateResponse(request, "services/_pricing_breakdown.html", {"st": st})


class CalcEstimatedDaysView(LoginRequiredMixin, View):
    """
    HTMX: recibe work_schedule_id, calcula días estimados, guarda y devuelve
    el bloque de días actualizado dentro del detalle del ServiceTemplate.
    """

    def post(self, request, pk):
        from apps.accounts.models import WorkSchedule

        st = get_object_or_404(ServiceTemplate, pk=pk)
        schedule_id = request.POST.get("work_schedule")
        schedule = get_object_or_404(WorkSchedule, pk=schedule_id)

        days = _working_days_needed(st.estimated_hours, schedule.weekly_hours)
        st.estimated_days = Decimal(days)
        st.save(update_fields=["estimated_days"])

        context = {
            "service_template": st,
            "schedules": WorkSchedule.objects.filter(is_active=True).order_by("-weekly_hours"),
            "selected_schedule": schedule,
            "calc_days": days,
        }
        return TemplateResponse(request, "services/_calc_days_result.html", context)
