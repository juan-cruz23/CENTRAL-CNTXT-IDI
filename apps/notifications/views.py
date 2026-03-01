from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.views.generic import ListView

from apps.notifications.models import Alert


class AlertListView(LoginRequiredMixin, ListView):
    """Shows the current user's alerts, filterable by severity/category/read status."""

    model = Alert
    template_name = "notifications/list.html"
    context_object_name = "alerts"
    paginate_by = 25

    def get_queryset(self):
        qs = Alert.objects.filter(
            target_users=self.request.user,
        ).select_related("project")

        # Filter by severity
        severity = self.request.GET.get("severity")
        if severity:
            qs = qs.filter(severity=severity)

        # Filter by category
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)

        # Filter by read status
        is_read = self.request.GET.get("is_read")
        if is_read == "true":
            qs = qs.filter(is_read=True)
        elif is_read == "false":
            qs = qs.filter(is_read=False)

        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["severity_choices"] = Alert.Severity.choices
        context["category_choices"] = Alert.Category.choices
        context["current_severity"] = self.request.GET.get("severity", "")
        context["current_category"] = self.request.GET.get("category", "")
        context["current_is_read"] = self.request.GET.get("is_read", "")
        return context


@login_required
@require_POST
def mark_as_read(request, pk):
    """POST view that marks an alert as read. HTMX compatible."""
    alert = get_object_or_404(Alert, pk=pk, target_users=request.user)
    alert.is_read = True
    alert.save(update_fields=["is_read", "updated_at"])

    # Return minimal HTML for HTMX swap
    if request.headers.get("HX-Request"):
        return HttpResponse(
            '<span class="badge bg-secondary">Leída</span>',
            content_type="text/html",
        )
    return HttpResponse(status=204)


@login_required
@require_POST
def mark_as_resolved(request, pk):
    """POST view that marks an alert as resolved."""
    alert = get_object_or_404(Alert, pk=pk, target_users=request.user)
    alert.is_resolved = True
    alert.resolved_at = timezone.now()
    alert.resolved_by = request.user
    alert.save(update_fields=["is_resolved", "resolved_at", "resolved_by", "updated_at"])

    # Return minimal HTML for HTMX swap
    if request.headers.get("HX-Request"):
        return HttpResponse(
            '<span class="badge bg-success">Resuelta</span>',
            content_type="text/html",
        )
    return HttpResponse(status=204)
