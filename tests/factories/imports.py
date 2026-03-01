import factory
from django.core.files.uploadedfile import SimpleUploadedFile
from factory.django import DjangoModelFactory
from apps.imports.models import ImportJob
from tests.factories.accounts import UserFactory


class ImportJobFactory(DjangoModelFactory):
    class Meta:
        model = ImportJob

    uploaded_by = factory.SubFactory(UserFactory)
    file = factory.LazyFunction(
        lambda: SimpleUploadedFile("test.csv", b"col1,col2\nval1,val2", content_type="text/csv")
    )
    source_type = "COR_SHEET"
    status = "UPLOADED"
