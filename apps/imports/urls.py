from django.urls import path

from apps.imports.views import (
    ConfirmImportView,
    ImportWizardView,
    PreviewImportView,
    UploadCSVView,
)

app_name = "imports"

urlpatterns = [
    path("", ImportWizardView.as_view(), name="wizard"),
    path("subir/", UploadCSVView.as_view(), name="upload"),
    path("previa/<int:pk>/", PreviewImportView.as_view(), name="preview"),
    path("confirmar/<int:pk>/", ConfirmImportView.as_view(), name="confirm"),
]
