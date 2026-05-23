from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import ProtectedError, Q
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView

from apps.terceros.forms import ThirdPartyForm
from apps.terceros.models import ThirdParty


class StaffOrAdminRequiredMixin(UserPassesTestMixin):
    """Allow only staff users (or superusers) to perform sensitive actions."""

    def test_func(self):
        u = self.request.user
        return bool(u.is_authenticated and (u.is_staff or u.is_superuser))


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
        # Nota 4: solo staff/superusers ven el botón "Eliminar"
        u = self.request.user
        context["can_delete"] = bool(u.is_authenticated and (u.is_staff or u.is_superuser))
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


class ThirdPartyDeleteView(LoginRequiredMixin, StaffOrAdminRequiredMixin, DeleteView):
    """Delete a third party (terceros de prueba). Solo staff/superusers.

    Nota 4 issue #21: el cliente pidió poder eliminar terceros de prueba sin
    pasar por Django admin. Se restringe a staff para evitar borrados accidentales
    desde el rol de gestor de proyecto.
    """

    model = ThirdParty
    template_name = "terceros/thirdparty_confirm_delete.html"
    success_url = reverse_lazy("terceros:list")
    context_object_name = "third_party"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        tp = self.object
        ctx["project_count"] = tp.projects.count()
        ctx["contact_count"] = tp.contacts.count()
        return ctx

    def form_valid(self, form):
        tp = self.object
        # Bloqueo defensivo: si tiene proyectos asociados, no permitir borrado.
        # third_party FK en Project es SET_NULL pero el cliente espera limpieza
        # explícita para no perder trazabilidad accidentalmente.
        if tp.projects.exists():
            messages.error(
                self.request,
                f"No se puede eliminar '{tp.name}' porque tiene "
                f"{tp.projects.count()} proyecto(s) asociado(s). "
                "Reasigna o elimina esos proyectos primero.",
            )
            return redirect("terceros:detail", pk=tp.pk)
        try:
            response = super().form_valid(form)
            messages.success(self.request, f"Tercero '{tp.name}' eliminado.")
            return response
        except ProtectedError as exc:
            protected_repr = ", ".join(str(o)[:80] for o in list(exc.protected_set)[:5])
            messages.error(
                self.request,
                f"No se puede eliminar '{tp.name}' por referencias protegidas: "
                f"{protected_repr}.",
            )
            return redirect("terceros:detail", pk=tp.pk)
