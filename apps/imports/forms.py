from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.imports.models import ImportJob


class ImportUploadForm(DaisyUIFormMixin, forms.Form):
    """Form for uploading a CSV file for import."""

    file = forms.FileField(
        label="Archivo CSV",
        help_text="Seleccione un archivo CSV para importar.",
        widget=forms.ClearableFileInput(
            attrs={
                "accept": ".csv,.xlsx,.xls",
                "class": "form-control",
            }
        ),
    )
    source_type = forms.ChoiceField(
        label="Tipo de fuente",
        choices=ImportJob.SourceType.choices,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
