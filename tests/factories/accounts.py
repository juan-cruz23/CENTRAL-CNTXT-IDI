import factory
from factory.django import DjangoModelFactory
from apps.accounts.models import User, Role, UserRole


class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda o: f"{o.username}@cntxt.com.co")
    first_name = factory.Faker("first_name", locale="es_CO")
    last_name = factory.Faker("last_name", locale="es_CO")
    password = factory.PostGenerationMethodCall("set_password", "testpass123")
    is_active = True


class RoleFactory(DjangoModelFactory):
    class Meta:
        model = Role

    code = factory.Sequence(lambda n: f"R{n:02d}")
    name = factory.Faker("job", locale="es_CO")
    default_hourly_rate = factory.Faker("pydecimal", left_digits=5, right_digits=2, positive=True)


class UserRoleFactory(DjangoModelFactory):
    class Meta:
        model = UserRole

    user = factory.SubFactory(UserFactory)
    role = factory.SubFactory(RoleFactory)
    is_primary = True
