from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.terceros.models import ThirdParty


class ThirdPartyForm(DaisyUIFormMixin, forms.ModelForm):
    """Form for creating and editing third parties."""

    class Meta:
        model = ThirdParty
        fields = [
            "person_type",
            "name",
            "company",
            "document_type",
            "nit",
            "relationship_type",
            "client_category",
            "email",
            "phone",
            "city",
            "is_active",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class ThirdPartyFilterForm(DaisyUIFormMixin, forms.Form):
    """Filter form for the third party list."""

    q = forms.CharField(
        required=False,
        label="Buscar",
        widget=forms.TextInput(attrs={"placeholder": "Nombre o empresa..."}),
    )
    relationship_type = forms.ChoiceField(
        required=False,
        label="Tipo",
        choices=[("", "Todos")] + list(ThirdParty.RelationshipType.choices),
    )
    document_type = forms.ChoiceField(
        required=False,
        label="Tipo de documento",
        choices=[("", "Todos")] + list(ThirdParty.DocumentType.choices),
    )
    is_active = forms.ChoiceField(
        required=False,
        label="Estado",
        choices=[("", "Todos"), ("true", "Activos"), ("false", "Inactivos")],
    )
