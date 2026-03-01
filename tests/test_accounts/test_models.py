import pytest
from tests.factories.accounts import UserFactory, RoleFactory, UserRoleFactory


@pytest.mark.django_db
class TestUser:
    def test_create_user(self):
        user = UserFactory(first_name="David", last_name="López")
        assert user.pk is not None
        assert user.get_full_name() == "David López"

    def test_user_str(self):
        user = UserFactory(username="david", first_name="David", last_name="López")
        assert str(user) == "David López"


@pytest.mark.django_db
class TestRole:
    def test_create_role(self):
        role = RoleFactory(code="LA", name="Líder de Arquitectura")
        assert role.pk is not None
        assert str(role) == "LA - Líder de Arquitectura"

    def test_role_unique_code(self):
        RoleFactory(code="LA")
        with pytest.raises(Exception):
            RoleFactory(code="LA")


@pytest.mark.django_db
class TestUserRole:
    def test_create_user_role(self):
        user_role = UserRoleFactory()
        assert user_role.pk is not None
        assert user_role.is_primary is True
