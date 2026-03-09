from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView

from apps.projects.models import ServiceInstance
from apps.services.mixins import has_pricing_permission
from apps.services.models import PricingChangeRequest


class PricingChangeRequestListView(LoginRequiredMixin, ListView):
    """List pricing change requests."""

    model = PricingChangeRequest
    template_name = "services/pricing_change_request_list.html"
    context_object_name = "requests"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset().select_related(
            "service_instance__project", "requested_by", "reviewed_by",
        )
        status = self.request.GET.get("status")
        if status:
            qs = qs.filter(status=status)
        if not has_pricing_permission(self.request.user):
            qs = qs.filter(requested_by=self.request.user)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["status_choices"] = PricingChangeRequest.Status.choices
        context["current_status"] = self.request.GET.get("status", "")
        context["can_review"] = has_pricing_permission(self.request.user)
        return context


class PricingChangeRequestCreateView(LoginRequiredMixin, CreateView):
    """Create a pricing change request."""

    model = PricingChangeRequest
    template_name = "services/pricing_change_request_form.html"
    fields = ["proposed_unit_price", "proposed_projected_hours", "justification"]

    def dispatch(self, request, *args, **kwargs):
        self.service_instance = get_object_or_404(
            ServiceInstance, pk=self.kwargs["si_pk"]
        )
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["service_instance"] = self.service_instance
        return context

    def form_valid(self, form):
        form.instance.service_instance = self.service_instance
        form.instance.requested_by = self.request.user
        form.instance.current_unit_price = self.service_instance.unit_price
        form.instance.current_projected_hours = self.service_instance.projected_hours
        messages.success(self.request, "Solicitud de cambio de precio creada.")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("services:pricing_request_list")


class PricingChangeRequestReviewView(LoginRequiredMixin, DetailView):
    """Review (approve/reject) a pricing change request."""

    model = PricingChangeRequest
    template_name = "services/pricing_change_review.html"
    context_object_name = "pcr"

    def post(self, request, *args, **kwargs):
        pcr = self.get_object()

        if not has_pricing_permission(request.user):
            messages.error(request, "No tiene permisos para revisar solicitudes.")
            return redirect("services:pricing_request_list")

        if pcr.status != PricingChangeRequest.Status.PENDING:
            messages.error(request, "Esta solicitud ya fue revisada.")
            return redirect("services:pricing_request_list")

        action = request.POST.get("action")
        review_notes = request.POST.get("review_notes", "")

        pcr.reviewed_by = request.user
        pcr.review_notes = review_notes
        pcr.reviewed_at = timezone.now()

        if action == "approve":
            pcr.status = PricingChangeRequest.Status.APPROVED
            # Apply proposed values to the service instance
            si = pcr.service_instance
            si.unit_price = pcr.proposed_unit_price
            si.projected_hours = pcr.proposed_projected_hours
            si.save()
            messages.success(request, "Solicitud aprobada. Valores actualizados.")
        elif action == "reject":
            pcr.status = PricingChangeRequest.Status.REJECTED
            messages.info(request, "Solicitud rechazada.")

        pcr.save()
        return redirect("services:pricing_request_list")
