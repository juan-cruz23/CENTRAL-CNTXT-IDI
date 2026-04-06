from django.contrib import admin

from apps.documents.models import DocumentTemplate, ProjectDocument


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "name",
        "document_type",
        "audience",
        "service_instance",
        "delivery_date",
        "approval_date",
    )
    list_filter = ("document_type", "audience", "project")
    search_fields = ("name", "notes")


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ("project_category", "name", "document_type", "audience", "is_required")
    list_filter = ("project_category", "document_type", "audience", "is_required")
    search_fields = ("name", "notes")
