from django import forms

from apps.capacity.models import ProjectAllocation, TeamMemberCapacity
from apps.common.forms import DaisyUIFormMixin
from apps.projects.models import Project, ServiceInstance


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
            "service_instance",
            "role",
            "start_date",
            "end_date",
            "weekly_hours",
            "allocation_pct",
            "notes",
        ]
        widgets = {
            "user": forms.Select(attrs={
                "class": "form-select",
                "hx-get": "/capacidad/validar-asignacion/",
                "hx-target": "#allocation-warning",
                "hx-trigger": "change",
                "hx-include": "[name='user'], [name='weekly_hours']",
            }),
            "project": forms.Select(attrs={
                "class": "form-select",
                "hx-get": "/capacidad/servicios-opciones/",
                "hx-target": "#id_service_instance",
                "hx-trigger": "change",
                "hx-include": "[name='project']",
            }),
            "service_instance": forms.Select(attrs={"class": "form-select"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "start_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "end_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "weekly_hours": forms.NumberInput(
                attrs={
                    "class": "form-control",
                    "step": "1",
                    "min": "1",
                    "max": "60",
                    "hx-get": "/capacidad/validar-asignacion/",
                    "hx-target": "#allocation-warning",
                    "hx-trigger": "change",
                    "hx-include": "[name='user'], [name='weekly_hours']",
                }
            ),
            "allocation_pct": forms.NumberInput(
                attrs={"class": "form-control", "step": "5", "min": "5", "max": "100"}
            ),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        initial_project = kwargs.pop("initial_project", None)
        super().__init__(*args, **kwargs)
        # Only show active projects
        self.fields["project"].queryset = Project.objects.filter(
            status=Project.Status.ACTIVE,
        ).order_by("code")
        # Only show users with a capacity record
        from apps.accounts.models import User

        users_with_capacity = TeamMemberCapacity.objects.values_list(
            "user_id", flat=True
        ).distinct()
        self.fields["user"].queryset = User.objects.filter(
            pk__in=users_with_capacity,
        ).order_by("first_name")
        # Service instance: optional, filtered by project
        self.fields["service_instance"].required = False
        self.fields["service_instance"].empty_label = "--- Opcional: vincular a servicio ---"
        if initial_project:
            try:
                project_pk = int(initial_project)
                self.initial["project"] = project_pk
                self.fields["service_instance"].queryset = ServiceInstance.objects.filter(
                    project_id=project_pk,
                ).order_by("code")
            except (ValueError, TypeError):
                self.fields["service_instance"].queryset = ServiceInstance.objects.none()
        else:
            self.fields["service_instance"].queryset = ServiceInstance.objects.none()
