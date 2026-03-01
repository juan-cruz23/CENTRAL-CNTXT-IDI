import pytest
from tests.factories import (
    ProjectFactory,
    ProjectPhaseInstanceFactory,
    ServiceInstanceFactory,
    MilestoneFactory,
    PaymentMilestoneFactory,
    ProjectMetricSnapshotFactory,
)


@pytest.fixture
def full_project(user):
    """Project with phase, service instance, milestone, payment, and metric snapshot."""
    proj = ProjectFactory(leader=user)
    phase = ProjectPhaseInstanceFactory(project=proj)
    si = ServiceInstanceFactory(project=proj, phase_instance=phase)
    milestone = MilestoneFactory(project=proj, phase_instance=phase)
    payment = PaymentMilestoneFactory(project=proj)
    snapshot = ProjectMetricSnapshotFactory(project=proj)
    return proj
