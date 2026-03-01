from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.capacity.models import ProjectAllocation, TeamMemberCapacity


class TeamMemberCapacityForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = TeamMemberCapacity
        fields = [
            "user",
            "weekly_available_hours",
            "effective_from",
            "effective_until",
            "notes",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "weekly_available_hours": forms.NumberInput(attrs={"class": "form-control"}),
            "effective_from": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "effective_until": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class ProjectAllocationForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = ProjectAllocation
        fields = [
            "user",
            "project",
            "role",
            "start_date",
            "end_date",
            "weekly_hours",
            "allocation_pct",
            "notes",
        ]
        widgets = {
            "user": forms.Select(attrs={"class": "form-select"}),
            "project": forms.Select(attrs={"class": "form-select"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "weekly_hours": forms.NumberInput(attrs={"class": "form-control"}),
            "allocation_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
