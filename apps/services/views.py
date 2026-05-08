from collections import OrderedDict
from datetime import date, timedelta
from decimal import Decimal
from math import ceil

from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Sum
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
from apps.services.forms import DeliverableForm, HardwareForm, HardwareMaintenanceForm, KeyActivityForm, KeyActivityInlineForm, ProjectCategoryForm, ProjectPhaseForm, ServiceActivityForm, ServiceSubCategoryForm, ServiceTemplateForm, SoftwareForm, SoftwarePaymentForm, action_inline_formset, deliverable_inline_formset, keyactivity_inline_formset
from apps.services.mixins import has_pricing_permission
from apps.services.models import (
    Deliverable,
    Hardware,
    HardwareMaintenance,
    KeyActivity,
    ProjectCategory,
    ProjectPhase,
    ServiceActivity,
    ServiceSubCategory,
    ServiceTemplate,
    Software,
    SoftwarePayment,
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

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        from django.db.models import Max, Sum
        totals = qs.aggregate(
            total_val=Sum("value"),
            total_dep=Sum("depreciation_per_hour"),
        )
        ctx["total_value"] = totals["total_val"] or 0
        ctx["total_depreciation"] = totals["total_dep"] or 0
        ctx["maint_by_hw"] = {
            m["hardware_id"]: m
            for m in HardwareMaintenance.objects.values("hardware_id").annotate(
                last_date=Max("date"),
                next_date=Max("next_maintenance_date"),
            )
        }
        return ctx


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


class HardwareMaintenanceView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = "services/hardware_maintenance.html"

    def get_hardware(self, pk):
        return get_object_or_404(Hardware, pk=pk)

    def get(self, request, pk):
        hw = self.get_hardware(pk)
        maintenances = hw.maintenances.all()
        import datetime
        form = HardwareMaintenanceForm(initial={"date": datetime.date.today()})
        from django.db.models import Sum
        total_cost = maintenances.aggregate(t=Sum("cost"))["t"] or 0
        return TemplateResponse(request, self.template_name, {
            "hardware": hw, "maintenances": maintenances, "form": form, "total_cost": total_cost,
        })

    def post(self, request, pk):
        hw = self.get_hardware(pk)
        form = HardwareMaintenanceForm(request.POST)
        if form.is_valid():
            m = form.save(commit=False)
            m.hardware = hw
            m.save()
        maintenances = hw.maintenances.all()
        from django.db.models import Sum
        total_cost = maintenances.aggregate(t=Sum("cost"))["t"] or 0
        return TemplateResponse(request, self.template_name, {
            "hardware": hw, "maintenances": maintenances,
            "form": HardwareMaintenanceForm(), "total_cost": total_cost,
        })


class HardwareMaintenanceDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        from django.shortcuts import redirect
        m = get_object_or_404(HardwareMaintenance, pk=pk)
        hw_pk = m.hardware_id
        m.delete()
        return redirect("services:hardware_maintenance", pk=hw_pk)
    success_url = reverse_lazy("services:hardware_list")


class SoftwareListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Software
    template_name = "services/software_list.html"
    context_object_name = "software_list"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        qs = self.get_queryset()
        from django.db.models import Max, Sum
        totals = qs.aggregate(
            total_annual=Sum("annual_value"),
            total_hourly=Sum("hourly_value"),
        )
        ctx["total_annual_value"] = totals["total_annual"] or 0
        ctx["total_hourly_value"] = totals["total_hourly"] or 0
        # Último pago y total pagado por software
        from django.db.models import Q
        from django.utils import timezone
        year = timezone.now().year
        payments_by_sw = {
            p["software_id"]: p
            for p in SoftwarePayment.objects.values("software_id").annotate(
                last_payment=Max("payment_date"),
                total_paid=Sum("amount"),
                total_paid_year=Sum("amount", filter=Q(payment_date__year=year)),
            )
        }
        ctx["payments_by_sw"] = payments_by_sw
        return ctx


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


class SoftwarePaymentHistoryView(LoginRequiredMixin, StaffRequiredMixin, View):
    template_name = "services/software_payments.html"

    def get_software(self, pk):
        return get_object_or_404(Software, pk=pk)

    def get(self, request, pk):
        sw = self.get_software(pk)
        payments = sw.payments.all()
        form = SoftwarePaymentForm(initial={"payment_date": __import__("datetime").date.today()})
        from django.db.models import Sum
        total = payments.aggregate(t=Sum("amount"))["t"] or 0
        return TemplateResponse(request, self.template_name, {
            "software": sw, "payments": payments, "form": form, "total_paid": total,
        })

    def post(self, request, pk):
        sw = self.get_software(pk)
        form = SoftwarePaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.software = sw
            payment.save()
            new_exp = form.cleaned_data.get("new_expiration_date")
            if new_exp:
                sw.expiration_date = new_exp
                sw.save(update_fields=["expiration_date"])
        payments = sw.payments.all()
        from django.db.models import Sum
        total = payments.aggregate(t=Sum("amount"))["t"] or 0
        return TemplateResponse(request, self.template_name, {
            "software": sw, "payments": payments, "form": SoftwarePaymentForm(), "total_paid": total,
        })


class SoftwarePaymentDeleteView(LoginRequiredMixin, StaffRequiredMixin, View):
    def post(self, request, pk):
        payment = get_object_or_404(SoftwarePayment, pk=pk)
        sw_pk = payment.software_id
        payment.delete()
        from django.shortcuts import redirect
        return redirect("services:software_payments", pk=sw_pk)


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


class ServiceActivityListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = ServiceActivity
    template_name = "services/serviceactivity_list.html"
    context_object_name = "actions"
    paginate_by = 50

    def get_queryset(self):
        qs = ServiceActivity.objects.select_related(
            "service_template", "key_activity__deliverable", "responsible_role"
        ).order_by("service_template__code", "key_activity__deliverable__name", "key_activity__name", "order")
        code = self.request.GET.get("q", "").strip()
        if code:
            qs = qs.filter(service_template__code__icontains=code)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["q"] = self.request.GET.get("q", "")
        return ctx


class ServiceActivityCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = ServiceActivity
    form_class = ServiceActivityForm
    template_name = "services/serviceactivity_form.html"
    success_url = reverse_lazy("services:serviceactivity_list")


class ServiceActivityUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = ServiceActivity
    form_class = ServiceActivityForm
    template_name = "services/serviceactivity_form.html"
    success_url = reverse_lazy("services:serviceactivity_list")


class ServiceActivityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = ServiceActivity
    template_name = "services/serviceactivity_confirm_delete.html"
    success_url = reverse_lazy("services:serviceactivity_list")


class ServiceTemplateListView(LoginRequiredMixin, ListView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_list.html"
    context_object_name = "service_templates"

    def get_queryset(self):
        qs = ServiceTemplate.objects.select_related(
            "category", "phase", "operative_line", "subcategory"
        ).order_by("operative_line__code", "category__code", "code")
        line = self.request.GET.get("line", "")
        phase = self.request.GET.get("phase", "")
        category = self.request.GET.get("category", "")
        q = self.request.GET.get("q", "")
        if line:
            qs = qs.filter(operative_line__pk=line)
        if phase:
            qs = qs.filter(phase__pk=phase)
        if category:
            qs = qs.filter(category__pk=category)
        if q:
            qs = qs.filter(code__icontains=q) | qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        from apps.organizations.models import OperativeLine
        context = super().get_context_data(**kwargs)
        context["create_url"] = reverse_lazy("services:servicetemplate_create")
        context["operative_lines"] = OperativeLine.objects.filter(is_active=True).order_by("code")
        context["phases"] = ProjectPhase.objects.all().order_by("number")
        context["categories"] = ProjectCategory.objects.filter(is_active=True).order_by("code")
        context["current_line"] = self.request.GET.get("line", "")
        context["current_phase"] = self.request.GET.get("phase", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["q"] = self.request.GET.get("q", "")
        return context


class ServiceTemplateDetailView(LoginRequiredMixin, DetailView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_detail.html"
    context_object_name = "service_template"

    def get_context_data(self, **kwargs):
        from collections import defaultdict
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

        # Full tree: Deliverable → KeyActivity → Actions
        deliverables = (
            st.deliverables
            .prefetch_related("key_activities__actions__responsible_role")
            .order_by("order", "name")
        )
        context["deliverables_tree"] = deliverables

        # Role summary across all actions
        role_summary = defaultdict(lambda: {"code": "", "name": "", "rate": Decimal(0), "hours": Decimal(0)})
        for deliv in deliverables:
            for kact in deliv.key_activities.all():
                for act in kact.actions.all():
                    if act.responsible_role_id:
                        r = act.responsible_role
                        entry = role_summary[act.responsible_role_id]
                        entry["code"] = r.code or r.name
                        entry["name"] = r.name
                        entry["rate"] = r.default_hourly_rate
                        entry["hours"] += act.estimated_hours or Decimal(0)
        for entry in role_summary.values():
            entry["total"] = entry["hours"] * entry["rate"]
        context["role_summary"] = sorted(role_summary.values(), key=lambda e: -e["hours"])
        # Counts for stats badges
        from apps.services.models import KeyActivity
        context["kact_count"] = KeyActivity.objects.filter(deliverable__service_template=st).count()
        return context


def _deliverable_defaults():
    """Returns {name: {unit, quantity}} using the most frequent unit per name."""
    from collections import Counter
    rows = Deliverable.objects.values("name", "unit", "quantity")
    counts = {}
    for r in rows:
        key = r["name"]
        pair = (r["unit"], str(r["quantity"]))
        counts.setdefault(key, Counter())[pair] += 1
    result = {}
    for name, counter in counts.items():
        unit, quantity = counter.most_common(1)[0][0]
        result[name] = {"unit": unit, "quantity": quantity}
    return result


def _role_rates_json():
    """Returns a JSON-serializable dict {role_pk: default_hourly_rate} for all active roles."""
    import json
    from apps.accounts.models import Role
    rates = {str(r.pk): str(r.default_hourly_rate) for r in Role.objects.filter(is_active=True)}
    return json.dumps(rates)


def _deliverable_kact_map():
    """Returns {deliverable_name: [sorted unique key activity names]}."""
    from collections import defaultdict
    result = defaultdict(set)
    for row in KeyActivity.objects.select_related("deliverable").values("deliverable__name", "name"):
        result[row["deliverable__name"]].add(row["name"])
    return {k: sorted(v) for k, v in result.items()}


def _kact_act_map():
    """Returns {key_activity_name: [sorted unique action names]}."""
    from collections import defaultdict
    result = defaultdict(set)
    for row in ServiceActivity.objects.filter(key_activity__isnull=False).values("key_activity__name", "name"):
        result[row["key_activity__name"]].add(row["name"])
    return {k: sorted(v) for k, v in result.items()}


def _parse_nested_activities_post(post_data):
    """Scan POST keys for ``kact-{di}-...`` and ``act-{di}-{ji}-{ki}-...``.

    Returns a dict ``{di: [{order, name, id, delete, actions: [{order, name, id, role, hours, delete}]}]}``
    keyed by deliverable index found in the POST. Used both to persist the nested
    activities and to repaint them on validation errors.
    """
    import re

    kact_re = re.compile(r"^kact-(\d+)-(\d+)-name$")
    by_deliv = {}
    for key in post_data.keys():
        m = kact_re.match(key)
        if not m:
            continue
        di, ji = int(m.group(1)), int(m.group(2))
        kp = f"kact-{di}-{ji}"
        kact_entry = {
            "index": ji,
            "id": post_data.get(f"{kp}-id") or "",
            "name": (post_data.get(f"{kp}-name") or "").strip(),
            "order": post_data.get(f"{kp}-order") or (ji + 1),
            "delete": bool(post_data.get(f"{kp}-DELETE")),
            "actions": [],
        }
        act_re = re.compile(rf"^act-{di}-{ji}-(\d+)-name$")
        for akey in post_data.keys():
            am = act_re.match(akey)
            if not am:
                continue
            ki = int(am.group(1))
            ap = f"act-{di}-{ji}-{ki}"
            kact_entry["actions"].append({
                "index": ki,
                "id": post_data.get(f"{ap}-id") or "",
                "name": (post_data.get(f"{ap}-name") or "").strip(),
                "order": post_data.get(f"{ap}-order") or (ki + 1),
                "role": post_data.get(f"{ap}-responsible_role") or "",
                "hours": post_data.get(f"{ap}-estimated_hours") or "",
                "delete": bool(post_data.get(f"{ap}-DELETE")),
            })
        kact_entry["actions"].sort(key=lambda a: a["index"])
        by_deliv.setdefault(di, []).append(kact_entry)
    for di in by_deliv:
        by_deliv[di].sort(key=lambda k: k["index"])
    return by_deliv


def _save_nested_activities(request, deliverable_formset):
    """Parse and save key activities + actions nested inside the deliverable formset POST data.

    Maps each POST deliverable index (``di``) to the matching saved Deliverable
    instance. Uses the formset order for the lookup, but skips DELETE-marked
    forms so JS-added items still align.
    """
    from apps.services.models import KeyActivity, ServiceActivity

    nested = _parse_nested_activities_post(request.POST)
    if not nested:
        return

    deliv_by_index = {}
    for i, deliv_form in enumerate(deliverable_formset.forms):
        cleaned = getattr(deliv_form, "cleaned_data", None) or {}
        if cleaned.get("DELETE"):
            continue
        if deliv_form.instance.pk:
            deliv_by_index[i] = deliv_form.instance

    for di, kacts in nested.items():
        deliv = deliv_by_index.get(di)
        if not deliv:
            continue
        for kact_entry in kacts:
            if kact_entry["delete"]:
                if kact_entry["id"]:
                    KeyActivity.objects.filter(pk=kact_entry["id"], deliverable=deliv).delete()
                continue
            if not kact_entry["name"]:
                continue
            if kact_entry["id"]:
                try:
                    kact = KeyActivity.objects.get(pk=kact_entry["id"], deliverable=deliv)
                    kact.name = kact_entry["name"]
                    kact.order = kact_entry["order"]
                    kact.save()
                except KeyActivity.DoesNotExist:
                    kact = KeyActivity.objects.create(
                        deliverable=deliv, name=kact_entry["name"], order=kact_entry["order"]
                    )
            else:
                kact = KeyActivity.objects.create(
                    deliverable=deliv, name=kact_entry["name"], order=kact_entry["order"]
                )

            for act_entry in kact_entry["actions"]:
                if act_entry["delete"]:
                    if act_entry["id"]:
                        ServiceActivity.objects.filter(pk=act_entry["id"], key_activity=kact).delete()
                    continue
                if not act_entry["name"]:
                    continue
                arole = act_entry["role"] or None
                ahours = act_entry["hours"] or 0
                if act_entry["id"]:
                    try:
                        act = ServiceActivity.objects.get(pk=act_entry["id"], key_activity=kact)
                        act.name = act_entry["name"]
                        act.order = act_entry["order"]
                        act.responsible_role_id = arole
                        act.estimated_hours = ahours
                        act.save()
                    except ServiceActivity.DoesNotExist:
                        ServiceActivity.objects.create(
                            service_template=deliv.service_template, key_activity=kact,
                            name=act_entry["name"], order=act_entry["order"],
                            responsible_role_id=arole, estimated_hours=ahours,
                        )
                else:
                    ServiceActivity.objects.create(
                        service_template=deliv.service_template, key_activity=kact,
                        name=act_entry["name"], order=act_entry["order"],
                        responsible_role_id=arole, estimated_hours=ahours,
                    )


class ServiceTemplateCreateView(LoginRequiredMixin, CreateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_rates_json"] = _role_rates_json()
        context["form_categories"] = ProjectCategory.objects.none()
        context["form_subcategories"] = ServiceSubCategory.objects.none()
        if "deliverable_formset" not in context:
            context["deliverable_formset"] = deliverable_inline_formset()
        context["deliverable_names"] = list(
            Deliverable.objects.values_list("name", flat=True).distinct().order_by("name")
        )
        context["deliverable_defaults"] = _deliverable_defaults()
        context["deliv_kact_map"] = _deliverable_kact_map()
        context["kact_act_map"] = _kact_act_map()
        context["selected_hardwares"] = []
        context["selected_softwares"] = []
        from apps.accounts.models import Role
        context["roles"] = list(Role.objects.filter(is_active=True).order_by("name").values("pk", "name", "code", "default_hourly_rate"))
        hw_items = list(Hardware.objects.filter(is_active=True).values("name", "depreciation_per_hour"))
        sw_items = list(Software.objects.filter(is_active=True).values("name", "hourly_value"))
        context["hw_items"] = hw_items
        context["sw_items"] = sw_items
        context["hw_rate_total"] = sum(float(h["depreciation_per_hour"]) for h in hw_items)
        context["sw_rate_total"] = sum(float(s["hourly_value"]) for s in sw_items)
        if self.request.method == "POST":
            context["nested_activities_data"] = _parse_nested_activities_post(self.request.POST)
        else:
            context["nested_activities_data"] = {}
        return context

    def post(self, request, *args, **kwargs):
        self.object = None
        form = self.get_form()
        formset = deliverable_inline_formset(data=request.POST)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.instance = self.object
            formset.save()
            _save_nested_activities(request, formset)
            return self.form_valid(form)
        return self.render_to_response(self.get_context_data(form=form, deliverable_formset=formset))


class ServiceTemplateUpdateView(LoginRequiredMixin, UpdateView):
    model = ServiceTemplate
    form_class = ServiceTemplateForm
    template_name = "services/servicetemplate_form.html"
    success_url = reverse_lazy("services:servicetemplate_list")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["role_rates_json"] = _role_rates_json()
        st = self.object
        if st.operative_line_id:
            context["form_categories"] = ProjectCategory.objects.filter(
                operative_line_id=st.operative_line_id
            ).order_by("code")
            context["form_subcategories"] = ServiceSubCategory.objects.filter(
                operative_line_id=st.operative_line_id, is_active=True
            ).order_by("code")
        else:
            context["form_categories"] = ProjectCategory.objects.none()
            context["form_subcategories"] = ServiceSubCategory.objects.none()
        if "deliverable_formset" not in context:
            context["deliverable_formset"] = deliverable_inline_formset(instance=st)
        context["deliverable_names"] = list(
            Deliverable.objects.values_list("name", flat=True).distinct().order_by("name")
        )
        context["deliverable_defaults"] = _deliverable_defaults()
        context["deliv_kact_map"] = _deliverable_kact_map()
        context["kact_act_map"] = _kact_act_map()
        context["selected_hardwares"] = list(st.hardwares.all()) if st.pk else []
        context["selected_softwares"] = list(st.softwares.all()) if st.pk else []
        from apps.accounts.models import Role
        context["roles"] = list(Role.objects.filter(is_active=True).order_by("name").values("pk", "name", "code", "default_hourly_rate"))
        hw_items = list(Hardware.objects.filter(is_active=True).values("name", "depreciation_per_hour"))
        sw_items = list(Software.objects.filter(is_active=True).values("name", "hourly_value"))
        context["hw_items"] = hw_items
        context["sw_items"] = sw_items
        context["hw_rate_total"] = sum(float(h["depreciation_per_hour"]) for h in hw_items)
        context["sw_rate_total"] = sum(float(s["hourly_value"]) for s in sw_items)
        if self.request.method == "POST":
            context["nested_activities_data"] = _parse_nested_activities_post(self.request.POST)
        else:
            context["nested_activities_data"] = {}
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        formset = deliverable_inline_formset(instance=self.object, data=request.POST)
        if form.is_valid() and formset.is_valid():
            self.object = form.save()
            formset.save()
            _save_nested_activities(request, formset)
            return self.form_valid(form)
        return self.render_to_response(self.get_context_data(form=form, deliverable_formset=formset))


class ServiceTemplateDeleteView(LoginRequiredMixin, DeleteView):
    model = ServiceTemplate
    template_name = "services/servicetemplate_confirm_delete.html"
    success_url = reverse_lazy("services:servicetemplate_list")


class DeliverableActivitiesView(LoginRequiredMixin, View):
    """Manages key activities for a deliverable.

    - Regular GET/POST: full page (deliverable_activities.html)
    - HTMX GET/POST: inline panel partial (_deliverable_activities_panel.html)
    """

    full_template   = "services/deliverable_activities.html"
    panel_template  = "services/_deliverable_activities_panel.html"

    def _is_htmx(self, request):
        return request.headers.get("HX-Request") == "true"

    def _prefix(self, pk):
        return f"kact-{pk}"

    def _context(self, deliverable, formset=None, saved=False):
        pk = deliverable.pk
        prefix = self._prefix(pk)
        kactivities = deliverable.key_activities.prefetch_related("actions").order_by("order", "name")
        from apps.accounts.models import Role
        role_choices = [(r.pk, str(r)) for r in Role.objects.filter(is_active=True).order_by("name")]
        return {
            "deliverable": deliverable,
            "kactivities": kactivities,
            "formset": formset or keyactivity_inline_formset(instance=deliverable, prefix=prefix),
            "prefix": prefix,
            "saved": saved,
            "role_choices": role_choices,
        }

    def get(self, request, pk):
        deliverable = get_object_or_404(Deliverable.objects.select_related("service_template"), pk=pk)
        tmpl = self.panel_template if self._is_htmx(request) else self.full_template
        return TemplateResponse(request, tmpl, self._context(deliverable))

    def post(self, request, pk):
        deliverable = get_object_or_404(Deliverable.objects.select_related("service_template"), pk=pk)
        prefix = self._prefix(pk)
        formset = keyactivity_inline_formset(instance=deliverable, data=request.POST, prefix=prefix)
        if formset.is_valid():
            formset.save()
            if self._is_htmx(request):
                return TemplateResponse(request, self.panel_template, self._context(deliverable, saved=True))
            from django.http import HttpResponseRedirect
            from django.urls import reverse
            return HttpResponseRedirect(reverse("services:deliverable_activities", args=[pk]))
        tmpl = self.panel_template if self._is_htmx(request) else self.full_template
        return TemplateResponse(request, tmpl, self._context(deliverable, formset))


class KeyActivityActionsView(LoginRequiredMixin, View):
    """HTMX partial + POST to manage actions for a key activity."""

    def _role_choices(self):
        from apps.accounts.models import Role
        return [(r.pk, str(r)) for r in Role.objects.filter(is_active=True).order_by("name")]

    def get(self, request, pk):
        kact = get_object_or_404(KeyActivity.objects.select_related("deliverable__service_template"), pk=pk)
        formset = action_inline_formset(instance=kact, prefix=f"actions-{pk}")
        return TemplateResponse(request, "services/_keyactivity_actions.html", {
            "kact": kact,
            "formset": formset,
            "role_choices": self._role_choices(),
        })

    def post(self, request, pk):
        kact = get_object_or_404(KeyActivity.objects.select_related("deliverable__service_template"), pk=pk)
        formset = action_inline_formset(instance=kact, data=request.POST, prefix=f"actions-{pk}")

        # Also set service_template on new actions
        if formset.is_valid():
            instances = formset.save(commit=False)
            for obj in instances:
                obj.service_template = kact.deliverable.service_template
                obj.key_activity = kact
                obj.save()
            for obj in formset.deleted_objects:
                obj.delete()
            return TemplateResponse(request, "services/_keyactivity_actions.html", {
                "kact": kact,
                "formset": action_inline_formset(instance=kact, prefix=f"actions-{pk}"),
                "saved": True,
                "role_choices": self._role_choices(),
            })
        return TemplateResponse(request, "services/_keyactivity_actions.html", {
            "kact": kact,
            "formset": formset,
            "role_choices": self._role_choices(),
        })


class FiltrarClasificacionView(LoginRequiredMixin, View):
    """HTMX partial: returns filtered category + subcategory selects for a given operative_line."""

    def get(self, request):
        line_id = request.GET.get("operative_line", "")
        selected_cat = request.GET.get("selected_cat", "")
        selected_sub = request.GET.get("selected_sub", "")

        if line_id:
            categories = ProjectCategory.objects.filter(operative_line_id=line_id).order_by("code")
            subcategories = ServiceSubCategory.objects.filter(
                operative_line_id=line_id, is_active=True
            ).order_by("code")
        else:
            categories = ProjectCategory.objects.none()
            subcategories = ServiceSubCategory.objects.none()

        return TemplateResponse(request, "services/_categoria_options.html", {
            "categories": categories,
            "selected_cat": selected_cat,
            "subcategories": subcategories,
            "selected_sub": selected_sub,
        })


# ---------------------------------------------------------------------------
# Pricing Dashboard
# ---------------------------------------------------------------------------


class PricingDashboardView(LoginRequiredMixin, ListView):
    model = ServiceTemplate
    template_name = "services/pricing_dashboard.html"
    context_object_name = "service_templates"

    def get_filters(self):
        return {
            "q": self.request.GET.get("q", "").strip(),
            "linea": self.request.GET.get("linea", "").strip(),
            "categoria": self.request.GET.get("categoria", "").strip(),
            "subcategoria": self.request.GET.get("subcategoria", "").strip(),
            "fase": self.request.GET.get("fase", "").strip(),
            "estado": self.request.GET.get("estado", "activos").strip(),
        }

    def get_queryset(self):
        qs = ServiceTemplate.objects.select_related(
            "category", "phase", "operative_line", "subcategory",
        )
        f = self.get_filters()

        if f["estado"] == "activos":
            qs = qs.filter(is_active=True)
        elif f["estado"] == "inactivos":
            qs = qs.filter(is_active=False)

        if f["q"]:
            from django.db.models import Q as DQ
            qs = qs.filter(DQ(name__icontains=f["q"]) | DQ(code__icontains=f["q"]))
        if f["linea"]:
            qs = qs.filter(operative_line__code=f["linea"])
        if f["categoria"]:
            qs = qs.filter(category_id=f["categoria"])
        if f["subcategoria"]:
            qs = qs.filter(subcategory_id=f["subcategoria"])
        if f["fase"]:
            qs = qs.filter(phase_id=f["fase"])

        return qs.order_by("category__code", "code")

    def get_context_data(self, **kwargs):
        from apps.organizations.models import OperativeLine
        from apps.services.models import ProjectCategory, ProjectPhase, ServiceSubCategory

        context = super().get_context_data(**kwargs)
        f = self.get_filters()
        qs = self.get_queryset()
        all_active = ServiceTemplate.objects.filter(is_active=True)

        # KPIs (basados en activos, sin importar otros filtros)
        context["total_services"] = all_active.count()
        context["total_hours"] = all_active.aggregate(h=Sum("estimated_hours"))["h"] or 0
        context["filtered_count"] = qs.count()

        # Por línea operativa (códigos reales de la BD)
        line_counts = {
            row["operative_line__code"]: row["c"]
            for row in all_active.values("operative_line__code").annotate(c=Count("pk"))
        }
        line_kpis = []
        for ol in OperativeLine.objects.all().order_by("code"):
            n = line_counts.get(ol.code, 0)
            if n > 0:
                line_kpis.append({"name": ol.name, "count": n})
        context["line_kpis"] = line_kpis
        context["kpi_cols"] = min(2 + len(line_kpis), 6)

        # Catálogos para los <select>
        context["operative_lines"] = OperativeLine.objects.all().order_by("code")
        cat_qs = ProjectCategory.objects.filter(is_active=True)
        sub_qs = ServiceSubCategory.objects.filter(is_active=True)
        if f["linea"]:
            cat_qs = cat_qs.filter(operative_line__code=f["linea"])
            sub_qs = sub_qs.filter(operative_line__code=f["linea"])
        context["categories"] = cat_qs.order_by("code")
        context["subcategories"] = sub_qs.order_by("code")
        context["phases"] = ProjectPhase.objects.all().order_by("number")

        # Group by category
        grouped = OrderedDict()
        for st in qs:
            cat_name = str(st.category) if st.category else "Sin categoría"
            grouped.setdefault(cat_name, []).append(st)
        context["grouped_services"] = list(grouped.items())

        context["filters"] = f
        context["has_filters"] = any(v for k, v in f.items() if k != "estado") or f["estado"] != "activos"
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


# ---------------------------------------------------------------------------
# Import / Export Excel
# ---------------------------------------------------------------------------

class ServiceTemplateExportView(LoginRequiredMixin, View):
    """GET → descarga Excel con todos los servicios."""

    def get(self, request):
        import io
        from apps.services.excel_io import export_services

        qs = ServiceTemplate.objects.all()
        # Filtro opcional por línea operativa
        line = request.GET.get("line")
        if line:
            qs = qs.filter(operative_line__code=line)

        wb = export_services(qs)

        buf = io.BytesIO()
        wb.save(buf)
        buf.seek(0)

        response = HttpResponse(
            buf.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = 'attachment; filename="servicios_export.xlsx"'
        return response


class ServiceTemplateImportView(LoginRequiredMixin, View):
    """GET → formulario de carga; POST → procesa el Excel."""

    template = "services/servicetemplate_import.html"

    def get(self, request):
        return TemplateResponse(request, self.template, {})

    def post(self, request):
        from apps.services.excel_io import import_services

        uploaded = request.FILES.get("excel_file")
        if not uploaded:
            return TemplateResponse(request, self.template, {"error": "No se adjuntó ningún archivo."})

        inactivate = request.POST.get("inactivate_missing") == "on"
        result = import_services(uploaded, inactivate_missing=inactivate)

        return TemplateResponse(request, self.template, {"result": result})


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
