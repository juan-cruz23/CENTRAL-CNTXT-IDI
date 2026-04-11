from django import forms

from apps.organizations.models import OperativeLine


class OperativeLineForm(forms.ModelForm):
    class Meta:
        model = OperativeLine
        fields = ["code", "name", "business_unit", "description", "is_active"]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 3, "class": "textarea textarea-bordered w-full"}),
            "code": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "name": forms.TextInput(attrs={"class": "input input-bordered w-full"}),
            "business_unit": forms.Select(attrs={"class": "select select-bordered w-full"}),
            "is_active": forms.CheckboxInput(attrs={"class": "checkbox"}),
        }
