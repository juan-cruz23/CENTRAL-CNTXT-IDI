from django.contrib import admin

from apps.documents.models import ProjectDocument


@admin.register(ProjectDocument)
class ProjectDocumentAdmin(admin.ModelAdmin):
    list_display = (
        "project",
        "name",
        "document_type",
        "service_instance",
        "delivery_date",
        "approval_date",
    )
    list_filter = ("document_type", "project")
    search_fields = ("name", "notes")
