import pytest
from django.db import connection
from django.test.utils import CaptureQueriesContext

from apps.services.excel_io import export_services
from apps.services.models import ServiceTemplate
from tests.factories.organizations import OperativeLineFactory
from tests.factories.services import ServiceTemplateFactory


@pytest.mark.django_db
class TestExportServicesQueryCount:
    """
    Regresión del 500 en `/servicios/templates/exportar/` (2026-05-20):
    la cascada de @property en ServiceTemplate llamaba a
    get_current_prorrateo_rate por cada fila del Excel, generando cientos
    de queries y disparando WORKER TIMEOUT en Cloud Run.
    """

    def test_export_does_not_explode_with_many_templates(self):
        line_a = OperativeLineFactory(code="MADE")
        line_b = OperativeLineFactory(code="SELECT")
        for i in range(20):
            ServiceTemplateFactory(operative_line=line_a if i % 2 == 0 else line_b)

        qs = ServiceTemplate.objects.all()
        with CaptureQueriesContext(connection) as ctx:
            wb = export_services(qs)

        assert wb is not None
        # 20 plantillas × 2 líneas operativas debe resolverse con un número
        # acotado de queries (prefetch + 1 lookup de prorrateo por línea).
        # Sin el fix la cascada supera fácilmente 200.
        assert len(ctx) < 20, (
            f"Export hizo {len(ctx)} queries para 20 plantillas — "
            f"posible regresión del N+1 de pricing"
        )
