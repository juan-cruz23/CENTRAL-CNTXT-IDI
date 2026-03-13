from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views import View
from django.views.generic import CreateView, ListView, UpdateView

from apps.documents.models import ProjectDocument


class ProjectDocumentListView(LoginRequiredMixin, ListView):
    model = ProjectDocument
    template_name = "documents/projectdocument_list.html"
    context_object_name = "documents"

    def get_template_names(self):
        if self.request.headers.get("HX-Request"):
            return ["documents/projectdocument_list_partial.html"]
        return [self.template_name]

    def get_queryset(self):
        return ProjectDocument.objects.filter(
            project_id=self.kwargs["project_pk"]
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        context["create_url"] = reverse(
            "documents:document_create",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )
        return context


class ProjectDocumentCreateView(LoginRequiredMixin, CreateView):
    model = ProjectDocument
    template_name = "documents/projectdocument_form.html"
    fields = [
        "project",
        "service_instance",
        "document_type",
        "name",
        "access_link",
        "file",
        "delivery_date",
        "approval_date",
        "notes",
    ]

    def get_initial(self):
        initial = super().get_initial()
        initial["project"] = self.kwargs["project_pk"]
        return initial

    def get_success_url(self):
        return reverse(
            "documents:document_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class ProjectDocumentUpdateView(LoginRequiredMixin, UpdateView):
    model = ProjectDocument
    template_name = "documents/projectdocument_form.html"
    fields = [
        "project",
        "service_instance",
        "document_type",
        "name",
        "access_link",
        "file",
        "delivery_date",
        "approval_date",
        "notes",
    ]

    def get_success_url(self):
        return reverse(
            "documents:document_list",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project_pk"] = self.kwargs["project_pk"]
        return context


class ProjectDocumentDeleteView(LoginRequiredMixin, View):
    """HTMX endpoint: delete a document."""

    def delete(self, request, project_pk, pk):
        doc = get_object_or_404(ProjectDocument, pk=pk, project_id=project_pk)
        doc.delete()
        return HttpResponse("")
