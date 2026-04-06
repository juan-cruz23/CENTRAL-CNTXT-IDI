from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.documents.models import ProjectDocument


class ProjectDocumentForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectDocument
        fields = ["document_type", "audience", "name", "access_link", "file", "delivery_date", "approval_date", "notes"]
        widgets = {
            "delivery_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "approval_date": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in ("delivery_date", "approval_date"):
            self.fields[f].input_formats = ["%Y-%m-%d"]
