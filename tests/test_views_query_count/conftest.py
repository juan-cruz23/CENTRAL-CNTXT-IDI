import pytest
from tests.factories import (
    PaymentMilestoneFactory,
    ProjectAllocationFactory,
    ProjectFactory,
    ProjectMetricSnapshotFactory,
    ProjectPhaseInstanceFactory,
    ServiceInstanceFactory,
    TeamMemberCapacityFactory,
    ClientFactory,
)


@pytest.fixture
def seeded_projects(user):
    """Create 10 projects with associated data for query count testing."""
    projects = []
    for _ in range(10):
        proj = ProjectFactory(status="ACTIVE")
        phase = ProjectPhaseInstanceFactory(project=proj)
        ServiceInstanceFactory(project=proj, phase_instance=phase)
        ServiceInstanceFactory(project=proj, phase_instance=phase)
        PaymentMilestoneFactory(project=proj)
        ProjectMetricSnapshotFactory(project=proj)
        projects.append(proj)

    # Add capacity data
    for i in range(3):
        cap = TeamMemberCapacityFactory()
        for proj in projects[:3]:
            ProjectAllocationFactory(user=cap.user, project=proj)

    return projects
