"""
Domain services for Project management.

Encapsulates business logic for creating, updating, and querying projects,
including progress/deviation recalculations and summary generation.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import QuerySet


class ProjectService:
    """High-level operations on Project entities."""

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")

    @staticmethod
    @transaction.atomic
    def create_project(data: dict):
        """
        Create a project together with its related prerequisite and phase
        instance records.

        Args:
            data: Dictionary containing:
                - project fields (code, name, client, status, etc.)
                - prerequisites: optional list[dict] of prerequisite data
                - phases: optional list[dict] of phase instance data

        Returns:
            The newly created Project instance.
        """
        from apps.projects.models import (
            Project,
            ProjectPhaseInstance,
            ProjectPrerequisite,
        )

        prerequisites_data = data.pop("prerequisites", [])
        phases_data = data.pop("phases", [])

        project = Project.objects.create(**data)

        # Bulk-create prerequisites
        if prerequisites_data:
            prerequisite_objects = [
                ProjectPrerequisite(project=project, **prereq)
                for prereq in prerequisites_data
            ]
            ProjectPrerequisite.objects.bulk_create(prerequisite_objects)

        # Bulk-create phase instances
        if phases_data:
            phase_objects = [
                ProjectPhaseInstance(project=project, **phase)
                for phase in phases_data
            ]
            ProjectPhaseInstance.objects.bulk_create(phase_objects)

        return project

    @classmethod
    def update_project_progress(cls, project_id: int):
        """
        Recalculate overall project progress from its service instances.

        Formula:
            progress = sum(si.total_value * si.progress_pct)
                       / sum(si.total_value)
            for all service instances belonging to the project.

        Returns:
            The updated Project instance.
        """
        from apps.projects.models import Project

        project = Project.objects.get(pk=project_id)
        service_instances = project.service_instances.all()

        total_weighted = cls.ZERO
        total_value = cls.ZERO

        for si in service_instances:
            si_value = Decimal(str(si.total_value or 0))
            si_progress = Decimal(str(si.progress_pct or 0))
            total_weighted += si_value * si_progress
            total_value += si_value

        if total_value > cls.ZERO:
            progress = (total_weighted / total_value).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
        else:
            progress = cls.ZERO

        project.current_progress_pct = progress
        project.save(update_fields=["current_progress_pct", "updated_at"])
        return project

    @classmethod
    def update_project_deviation(cls, project_id: int):
        """
        Calculate schedule deviation by comparing actual vs planned dates.

        When the project has planned start/end dates, deviation is computed
        as the percentage difference between the days actually elapsed
        (or total actual duration) versus the planned duration.

        Returns:
            The updated Project instance.
        """
        from apps.projects.models import Project

        project = Project.objects.get(pk=project_id)

        if not project.planned_start_date or not project.planned_end_date:
            project.schedule_deviation_pct = cls.ZERO
            project.save(update_fields=["schedule_deviation_pct", "updated_at"])
            return project

        planned_duration = (
            project.planned_end_date - project.planned_start_date
        ).days

        if planned_duration <= 0:
            project.schedule_deviation_pct = cls.ZERO
            project.save(update_fields=["schedule_deviation_pct", "updated_at"])
            return project

        # Determine actual reference date
        if project.actual_end_date:
            actual_end = project.actual_end_date
        else:
            actual_end = date.today()

        actual_start = project.actual_start_date or project.planned_start_date
        actual_elapsed = (actual_end - actual_start).days

        deviation = (
            Decimal(str(actual_elapsed - planned_duration))
            / Decimal(str(planned_duration))
            * cls.HUNDRED
        ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

        project.schedule_deviation_pct = deviation
        project.save(update_fields=["schedule_deviation_pct", "updated_at"])
        return project

    @staticmethod
    def get_active_projects() -> QuerySet:
        """
        Return active projects with optimised related-object loading.

        Returns:
            QuerySet of active Project instances.
        """
        from apps.projects.models import Project

        return (
            Project.objects.filter(status=Project.Status.ACTIVE)
            .select_related(
                "client",
                "category",
                "business_unit",
                "operative_line",
                "leader",
            )
            .prefetch_related(
                "phase_instances",
                "service_instances",
                "milestones",
                "payment_milestones",
            )
        )

    @classmethod
    def get_project_summary(cls, project_id: int) -> dict:
        """
        Build a comprehensive project summary including financial,
        schedule, and satisfaction metrics.

        Returns:
            dict with keys: project, progress, deviation, financial,
            phases, milestones, satisfaction.
        """
        from apps.projects.models import Project

        project = (
            Project.objects.select_related(
                "client",
                "category",
                "business_unit",
                "operative_line",
                "leader",
            )
            .prefetch_related(
                "phase_instances__phase",
                "phase_instances__service_instances",
                "service_instances",
                "milestones",
                "payment_milestones",
            )
            .get(pk=project_id)
        )

        # -- Financial summary --
        payment_milestones = project.payment_milestones.all()
        total_value = project.total_value or cls.ZERO
        total_collected = sum(
            (pm.collection_value or cls.ZERO) for pm in payment_milestones
        )
        total_executed = sum(
            (pm.executed_value or cls.ZERO) for pm in payment_milestones
        )

        # -- Phase breakdown --
        phases = []
        for pi in project.phase_instances.all():
            phases.append(
                {
                    "phase_id": pi.id,
                    "phase_name": str(pi.phase) if pi.phase_id else f"Fase {pi.order}",
                    "order": pi.order,
                    "progress_pct": float(pi.progress_pct or 0),
                    "total_value": float(pi.total_value or 0),
                    "planned_start_date": pi.planned_start_date,
                    "planned_end_date": pi.planned_end_date,
                    "actual_start_date": pi.actual_start_date,
                    "actual_end_date": pi.actual_end_date,
                }
            )

        # -- Milestones --
        milestones = []
        for m in project.milestones.all():
            milestones.append(
                {
                    "milestone_id": m.id,
                    "code": m.code,
                    "name": m.name,
                    "milestone_type": m.milestone_type,
                    "planned_date": m.planned_date,
                    "actual_date": m.actual_date,
                }
            )

        # -- Satisfaction (latest CVE) --
        satisfaction = {}
        try:
            latest_cve = project.satisfaction_measurements.order_by(
                "-measurement_date"
            ).first()
            if latest_cve:
                satisfaction["latest_cve_score"] = float(latest_cve.cve_score)
                satisfaction["latest_cve_date"] = latest_cve.measurement_date
        except Exception:
            pass

        return {
            "project": {
                "id": project.id,
                "code": project.code,
                "name": project.name,
                "status": project.status,
                "client": str(project.client) if project.client else None,
                "leader": str(project.leader) if project.leader else None,
                "planned_start_date": project.planned_start_date,
                "planned_end_date": project.planned_end_date,
                "actual_start_date": project.actual_start_date,
                "actual_end_date": project.actual_end_date,
            },
            "progress": float(project.current_progress_pct or 0),
            "deviation": float(project.schedule_deviation_pct or 0),
            "financial": {
                "total_value": float(total_value),
                "total_executed": float(total_executed),
                "total_collected": float(total_collected),
                "profitability_pct": float(project.profitability_pct or 0),
            },
            "phases": phases,
            "milestones": milestones,
            "satisfaction": satisfaction,
        }
