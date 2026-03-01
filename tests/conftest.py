import pytest
from tests.factories.accounts import UserFactory
from tests.factories.organizations import OrganizationalSystemFactory
from tests.factories.projects import ProjectFactory, ProjectPhaseInstanceFactory, ServiceInstanceFactory


@pytest.fixture
def user(db):
    return UserFactory()


@pytest.fixture
def admin_user(db):
    return UserFactory(is_staff=True, is_superuser=True)


@pytest.fixture
def authenticated_client(client, user):
    client.force_login(user)
    return client


@pytest.fixture
def admin_client(client, admin_user):
    client.force_login(admin_user)
    return client


@pytest.fixture
def project(db):
    return ProjectFactory()


@pytest.fixture
def project_with_phase(db):
    proj = ProjectFactory()
    phase = ProjectPhaseInstanceFactory(project=proj)
    return proj, phase


@pytest.fixture
def service_instance(db):
    proj = ProjectFactory()
    phase = ProjectPhaseInstanceFactory(project=proj)
    si = ServiceInstanceFactory(project=proj, phase_instance=phase)
    return si


@pytest.fixture
def organizational_system(db):
    return OrganizationalSystemFactory()
