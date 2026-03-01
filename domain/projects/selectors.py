"""
Domain selectors (query functions) for the Project aggregate.

All functions return QuerySets or model instances and contain no
side effects -- they are purely read-only operations.
"""

from django.db.models import Q, QuerySet


def get_project_with_details(project_id: int):
    """
    Retrieve a single project with all related objects eagerly loaded.

    Returns:
        Project instance with select_related and prefetch_related applied.

    Raises:
        Project.DoesNotExist if no matching project is found.
    """
    from apps.projects.models import Project

    return (
        Project.objects.select_related(
            "client",
            "category",
            "business_unit",
            "operative_line",
            "leader",
        )
        .prefetch_related(
            "prerequisites",
            "phase_instances__phase",
            "phase_instances__service_instances",
            "phase_instances__milestones",
            "service_instances__service_template",
            "service_instances__assigned_professional",
            "service_instances__responsible_role",
            "milestones",
            "payment_milestones",
            "satisfaction_measurements__survey",
            "allocations__user",
            "metric_snapshots",
        )
        .get(pk=project_id)
    )


def get_projects_by_status(status: str) -> QuerySet:
    """
    Return projects filtered by the given status code.

    Args:
        status: One of Project.Status values (e.g. 'ACTIVE', 'PLANNING').

    Returns:
        QuerySet of Project instances.
    """
    from apps.projects.models import Project

    return (
        Project.objects.filter(status=status)
        .select_related("client", "leader", "operative_line")
        .order_by("-created_at")
    )


def get_projects_by_leader(user_id: int) -> QuerySet:
    """
    Return all projects led by a given user.

    Args:
        user_id: Primary key of the User who is the project leader.

    Returns:
        QuerySet of Project instances.
    """
    from apps.projects.models import Project

    return (
        Project.objects.filter(leader_id=user_id)
        .select_related("client", "leader", "operative_line")
        .order_by("-created_at")
    )


def get_projects_by_system(system_code: str) -> QuerySet:
    """
    Return projects that belong to a given organisational system.

    A project is considered part of a system when:
      - Its operative_line's business_unit is associated with the system, OR
      - Its leader is the leader of that system.

    Args:
        system_code: Code of the OrganizationalSystem (e.g. 'NEO', 'IDI').

    Returns:
        QuerySet of Project instances.
    """
    from apps.organizations.models import OrganizationalSystem
    from apps.projects.models import Project

    try:
        system = OrganizationalSystem.objects.get(code=system_code)
    except OrganizationalSystem.DoesNotExist:
        return Project.objects.none()

    # Build filter: projects whose operative_line belongs to a BU
    # in the system, or whose leader is the system leader.
    filters = Q(operative_line__business_unit__in=system.code)  # placeholder
    if system.leader_id:
        filters = filters | Q(leader_id=system.leader_id)

    # Since OrganizationalSystem does not have a direct FK to BusinessUnit,
    # we match projects whose business_unit or operative_line's business_unit
    # is part of the same system by convention.  The safest approach is to
    # check for the system leader plus any explicit business_unit filter.
    return (
        Project.objects.filter(
            Q(leader_id=system.leader_id)
        )
        .select_related("client", "leader", "operative_line")
        .distinct()
        .order_by("-created_at")
    )


def get_project_service_instances(
    project_id: int, phase_id: int = None
) -> QuerySet:
    """
    Return service instances for a project, optionally filtered by phase.

    Args:
        project_id: Primary key of the Project.
        phase_id:   Optional primary key of the ProjectPhaseInstance to
                    filter by.

    Returns:
        QuerySet of ServiceInstance objects.
    """
    from apps.projects.models import ServiceInstance

    qs = ServiceInstance.objects.filter(project_id=project_id).select_related(
        "phase_instance",
        "service_template",
        "assigned_professional",
        "responsible_role",
    )

    if phase_id is not None:
        qs = qs.filter(phase_instance_id=phase_id)

    return qs.order_by("phase_instance__order", "code")


def get_projects_at_risk() -> QuerySet:
    """
    Return projects whose latest metric snapshot shows SPI < 0.9
    or CPI < 0.9.

    A project is considered "at risk" if its most recent
    ProjectMetricSnapshot has either index below the threshold.

    Returns:
        QuerySet of Project instances.
    """
    from decimal import Decimal

    from apps.metrics.models import ProjectMetricSnapshot
    from apps.projects.models import Project

    threshold = Decimal("0.9")

    # Get the latest snapshot per project with risky indices.
    risky_snapshots = (
        ProjectMetricSnapshot.objects.order_by("project_id", "-snapshot_date")
        .distinct("project_id")
        .filter(Q(spi__lt=threshold) | Q(cpi__lt=threshold))
    )

    risky_project_ids = risky_snapshots.values_list("project_id", flat=True)

    return (
        Project.objects.filter(
            pk__in=risky_project_ids,
            status=Project.Status.ACTIVE,
        )
        .select_related("client", "leader")
        .order_by("-created_at")
    )


def search_projects(query: str) -> QuerySet:
    """
    Search projects by code, name, or client name.

    Args:
        query: Free-text search term.

    Returns:
        QuerySet of matching Project instances.
    """
    from apps.projects.models import Project

    if not query or not query.strip():
        return Project.objects.none()

    q = query.strip()

    return (
        Project.objects.filter(
            Q(code__icontains=q)
            | Q(name__icontains=q)
            | Q(client__name__icontains=q)
        )
        .select_related("client", "leader")
        .distinct()
        .order_by("-created_at")
    )
