from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.rfis.models import RFI


class RFIListView(LoginRequiredMixin, ListView):
    model = RFI
    template_name = "rfis/rfi_list.html"
    context_object_name = "rfis"

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["rfis/rfi_list_partial.html"]
        return [self.template_name]

    def get_queryset(self):
        return RFI.objects.filter(project_id=self.kwargs["project_pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        context["create_url"] = reverse(
            "rfis:rfi_create",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )
        # Total hours for footer
        total_hours = RFI.objects.filter(
            project_id=self.kwargs["project_pk"]
        ).aggregate(total=Sum("time_invested_hours"))["total"]
        context["total_hours"] = total_hours or 0
        return context


class RFICreateView(LoginRequiredMixin, CreateView):
    model = RFI
    template_name = "rfis/rfi_form.html"
    fields = [
        "project",
        "service_instance",
        "code",
        "observations",
        "time_invested_hours",
        "professional",
        "status",
        "external_discipline",
        "response",
    ]

    def get_initial(self):
        initial = super().get_initial()
        initial["project"] = self.kwargs["project_pk"]
        return initial

    def get_success_url(self):
        return reverse(
            "rfis:rfi_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class RFIDetailView(LoginRequiredMixin, DetailView):
    model = RFI
    template_name = "rfis/rfi_detail.html"
    context_object_name = "rfi"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class RFIUpdateView(LoginRequiredMixin, UpdateView):
    model = RFI
    template_name = "rfis/rfi_form.html"
    fields = [
        "project",
        "service_instance",
        "code",
        "observations",
        "time_invested_hours",
        "professional",
        "status",
        "external_discipline",
        "response",
    ]

    def get_success_url(self):
        return reverse(
            "rfis:rfi_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class RFIDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete an RFI."""

    def delete(self, request, project_pk, pk):
        rfi = get_object_or_404(RFI, pk=pk, project_id=project_pk)
        rfi.delete()
        return HttpResponse("")
