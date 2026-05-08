from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from apps.terceros.forms import ThirdPartyForm
from apps.terceros.models import ThirdParty


class ThirdPartyListView(LoginRequiredMixin, ListView):
    """List third parties with filtering by type, search and status."""

    model = ThirdParty
    template_name = "terceros/thirdparty_list.html"
    context_object_name = "third_parties"
    paginate_by = 25

    def get_queryset(self):
        qs = super().get_queryset()
        search = self.request.GET.get("q")
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(company__icontains=search)
                | Q(nit__icontains=search)
            )
        relationship_type = self.request.GET.get("relationship_type")
        if relationship_type:
            qs = qs.filter(relationship_type=relationship_type)
        document_type = self.request.GET.get("document_type")
        if document_type:
            qs = qs.filter(document_type=document_type)
        is_active = self.request.GET.get("is_active")
        if is_active == "true":
            qs = qs.filter(is_active=True)
        elif is_active == "false":
            qs = qs.filter(is_active=False)
        return qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["relationship_types"] = ThirdParty.RelationshipType.choices
        context["document_types"] = ThirdParty.DocumentType.choices
        context["current_type"] = self.request.GET.get("relationship_type", "")
        context["current_document_type"] = self.request.GET.get("document_type", "")
        context["search_query"] = self.request.GET.get("q", "")
        context["current_active"] = self.request.GET.get("is_active", "")
        context["create_url"] = reverse_lazy("terceros:create")
        return context


class ThirdPartyDetailView(LoginRequiredMixin, DetailView):
    """Detail view for a third party with contacts and projects."""

    model = ThirdParty
    template_name = "terceros/thirdparty_detail.html"
    context_object_name = "third_party"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["contacts"] = self.object.contacts.all()
        context["projects"] = self.object.projects.select_related(
            "leader", "category",
        ).order_by("-created_at")
        return context


class ThirdPartyCreateView(LoginRequiredMixin, CreateView):
    """Create a new third party."""

    model = ThirdParty
    form_class = ThirdPartyForm
    template_name = "terceros/thirdparty_form.html"

    def get_success_url(self):
        return reverse_lazy("terceros:detail", kwargs={"pk": self.object.pk})


class ThirdPartyUpdateView(LoginRequiredMixin, UpdateView):
    """Update an existing third party."""

    model = ThirdParty
    form_class = ThirdPartyForm
    template_name = "terceros/thirdparty_form.html"

    def get_success_url(self):
        return reverse_lazy("terceros:detail", kwargs={"pk": self.object.pk})
