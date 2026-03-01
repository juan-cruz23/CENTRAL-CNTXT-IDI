"""
Domain events for the Project aggregate.

These functions represent side-effect triggers that should be called when
specific domain events occur.  They coordinate updates across aggregates
(e.g. recalculating project progress when a service instance changes).
"""

import logging

logger = logging.getLogger(__name__)


def on_service_instance_updated(service_instance_id: int) -> None:
    """
    Called when a ServiceInstance is created or updated.

    Side effects:
        1. Recalculates the parent project's overall progress.
        2. Recalculates the parent project's schedule deviation.

    Args:
        service_instance_id: Primary key of the updated ServiceInstance.
    """
    from apps.projects.models import ServiceInstance

    from domain.projects.services import ProjectService

    try:
        si = ServiceInstance.objects.select_related("project").get(
            pk=service_instance_id
        )
    except ServiceInstance.DoesNotExist:
        logger.warning(
            "on_service_instance_updated: ServiceInstance %s not found.",
            service_instance_id,
        )
        return

    project_id = si.project_id

    try:
        ProjectService.update_project_progress(project_id)
    except Exception:
        logger.exception(
            "Failed to update progress for project %s.", project_id
        )

    try:
        ProjectService.update_project_deviation(project_id)
    except Exception:
        logger.exception(
            "Failed to update deviation for project %s.", project_id
        )


def on_milestone_reached(milestone_id: int) -> None:
    """
    Called when a milestone's actual_date is set (i.e. the milestone
    has been reached).

    Side effects:
        1. Creates a notification alert for the project leader and
           team members.
        2. If the milestone is a FINAL_DELIVERY, transitions the
           project to COMPLETED status.

    Args:
        milestone_id: Primary key of the Milestone that was reached.
    """
    from apps.notifications.models import Alert
    from apps.projects.models import Milestone, Project

    try:
        milestone = Milestone.objects.select_related("project", "project__leader").get(
            pk=milestone_id
        )
    except Milestone.DoesNotExist:
        logger.warning(
            "on_milestone_reached: Milestone %s not found.", milestone_id
        )
        return

    project = milestone.project

    # Create notification alert
    alert = Alert.objects.create(
        project=project,
        severity=Alert.Severity.INFO,
        category=Alert.Category.MILESTONE_DUE,
        title=f"Hito alcanzado: {milestone.code} - {milestone.name}",
        message=(
            f'El hito "{milestone.name}" del proyecto {project.code} '
            f"ha sido completado el {milestone.actual_date}."
        ),
    )

    # Add the project leader as a target user if available
    if project.leader_id:
        alert.target_users.add(project.leader)

    # If this is a final delivery, mark the project as completed
    if milestone.milestone_type == Milestone.MilestoneType.FINAL_DELIVERY:
        old_status = project.status
        project.status = Project.Status.COMPLETED
        project.save(update_fields=["status", "updated_at"])

        on_project_status_changed(project.id, old_status, project.status)


def on_project_status_changed(
    project_id: int, old_status: str, new_status: str
) -> None:
    """
    Called when a project's status changes.

    Side effects:
        Creates a notification alert informing stakeholders of the
        status transition.

    Args:
        project_id: Primary key of the Project.
        old_status:  Previous status value.
        new_status:  New status value.
    """
    from apps.notifications.models import Alert
    from apps.projects.models import Project

    try:
        project = Project.objects.select_related("leader").get(pk=project_id)
    except Project.DoesNotExist:
        logger.warning(
            "on_project_status_changed: Project %s not found.", project_id
        )
        return

    # Determine severity based on the transition
    if new_status == Project.Status.CANCELLED:
        severity = Alert.Severity.CRITICAL
    elif new_status == Project.Status.PAUSED:
        severity = Alert.Severity.WARNING
    else:
        severity = Alert.Severity.INFO

    old_label = dict(Project.Status.choices).get(old_status, old_status)
    new_label = dict(Project.Status.choices).get(new_status, new_status)

    alert = Alert.objects.create(
        project=project,
        severity=severity,
        category=Alert.Category.SCHEDULE_DEVIATION,
        title=f"Cambio de estado: {project.code}",
        message=(
            f"El proyecto {project.code} - {project.name} cambió de estado "
            f'de "{old_label}" a "{new_label}".'
        ),
    )

    if project.leader_id:
        alert.target_users.add(project.leader)
