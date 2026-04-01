from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.http import JsonResponse
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.geography.forms import CountryForm, MunicipalityForm
from apps.geography.models import Country, Municipality


class StaffRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff


# ---------------------------------------------------------------------------
# Country views
# ---------------------------------------------------------------------------
class CountryListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Country
    template_name = "geography/country_list.html"
    context_object_name = "countries"

    def get_queryset(self):
        return Country.objects.annotate_municipality_count() if hasattr(Country.objects, 'annotate_municipality_count') else Country.objects.all()

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        from django.db.models import Count
        ctx["countries"] = Country.objects.annotate(mun_count=Count("municipalities")).order_by("name")
        return ctx


class CountryCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Country
    form_class = CountryForm
    template_name = "geography/country_form.html"
    success_url = reverse_lazy("geography:country_list")


class CountryUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Country
    form_class = CountryForm
    template_name = "geography/country_form.html"
    success_url = reverse_lazy("geography:country_list")


class CountryDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Country
    template_name = "geography/country_confirm_delete.html"
    success_url = reverse_lazy("geography:country_list")


# ---------------------------------------------------------------------------
# Municipality views
# ---------------------------------------------------------------------------
class MunicipalityListView(LoginRequiredMixin, StaffRequiredMixin, ListView):
    model = Municipality
    template_name = "geography/municipality_list.html"
    context_object_name = "municipalities"
    paginate_by = 50

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["geography/partials/municipality_rows.html"]
        return [self.template_name]

    def get_queryset(self):
        qs = Municipality.objects.select_related("country").order_by("department", "name")
        country_id = self.request.GET.get("country")
        department = self.request.GET.get("department")
        q = self.request.GET.get("q")
        if country_id:
            qs = qs.filter(country_id=country_id)
        if department:
            qs = qs.filter(department=department)
        if q:
            qs = qs.filter(name__icontains=q)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["countries"] = Country.objects.filter(is_active=True)
        ctx["departments"] = (
            Municipality.objects.values_list("department", flat=True)
            .distinct().order_by("department")
        )
        ctx["current_country"] = self.request.GET.get("country", "")
        ctx["current_department"] = self.request.GET.get("department", "")
        ctx["search_query"] = self.request.GET.get("q", "")
        return ctx


class MunicipalityCreateView(LoginRequiredMixin, StaffRequiredMixin, CreateView):
    model = Municipality
    form_class = MunicipalityForm
    template_name = "geography/municipality_form.html"
    success_url = reverse_lazy("geography:municipality_list")


class MunicipalityUpdateView(LoginRequiredMixin, StaffRequiredMixin, UpdateView):
    model = Municipality
    form_class = MunicipalityForm
    template_name = "geography/municipality_form.html"
    success_url = reverse_lazy("geography:municipality_list")


class MunicipalityDeleteView(LoginRequiredMixin, StaffRequiredMixin, DeleteView):
    model = Municipality
    template_name = "geography/municipality_confirm_delete.html"
    success_url = reverse_lazy("geography:municipality_list")


# ---------------------------------------------------------------------------
# HTMX endpoint: municipalities by country
# ---------------------------------------------------------------------------
def municipalities_by_country(request, country_id):
    """Return municipalities for a country as JSON (for HTMX select in project form)."""
    muns = (
        Municipality.objects
        .filter(country_id=country_id, is_active=True)
        .values("id", "name", "department")
        .order_by("department", "name")
    )
    return JsonResponse({"municipalities": list(muns)})
