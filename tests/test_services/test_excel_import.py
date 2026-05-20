import io

import pytest
from openpyxl import Workbook

from apps.services.excel_io import COLUMNS, import_services
from apps.services.models import KeyActivity, ServiceActivity, ServiceTemplate


def _wb_with_rows(rows):
    wb = Workbook()
    ws = wb.active
    ws.append(COLUMNS)
    for row in rows:
        full = [row.get(c, "") for c in COLUMNS]
        ws.append(full)
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf


@pytest.fixture
def base_categories(db):
    from apps.services.models import ProjectCategory, ProjectPhase

    ProjectCategory.objects.update_or_create(code="C1", defaults={"name": "Cat 1"})
    ProjectPhase.objects.update_or_create(number=1, defaults={"name": "Fase 1"})


@pytest.mark.django_db
class TestImportServices:
    def test_long_action_name_persists(self, base_categories):
        """Una acción con nombre >300 chars (caso real del cliente) debe
        guardarse — antes truncaba con `value too long for varying(300)`."""
        long_text = ("Kuula despues de la edición y corrección de las imágenes "
                     "se suben a la plataforma 360 de preferencia. ") * 5  # ~500 chars
        wb = _wb_with_rows([
            {
                "FASES": "Fase 1", "CÓDIGO": "S1", "CATEGORÍA": "Cat 1",
                "NOMBRE DE SERVICIO": "Servicio test",
                "ENTREGABLE": "Ent A", "UND ENTREGABLE": "Und", "CANTIDAD": "1",
                "ACTIVIDADES CLAVES": "Act A",
                "ACCIONES CLAVES": long_text,
                "TIEMPO (HORAS)": "1",
            }
        ])
        result = import_services(wb, inactivate_missing=False)
        assert result["created"] == 1, result["errors"]
        assert len(long_text) > 300  # confirma que excede el viejo varchar(300)
        assert ServiceActivity.objects.filter(name=long_text.strip()).exists()

    def test_one_bad_row_does_not_kill_the_rest(self, base_categories, monkeypatch):
        """Si una acción inserta-falla, las siguientes deben persistir igual
        (savepoints anidados aíslan cada fila bajo ATOMIC_REQUESTS)."""
        wb = _wb_with_rows([
            {
                "FASES": "Fase 1", "CÓDIGO": "S2", "CATEGORÍA": "Cat 1",
                "NOMBRE DE SERVICIO": "Servicio test 2",
                "ENTREGABLE": "Ent B", "UND ENTREGABLE": "Und", "CANTIDAD": "1",
                "ACTIVIDADES CLAVES": "Act B",
                "ACCIONES CLAVES": "Acción ok 1", "TIEMPO (HORAS)": "1",
            },
            {
                "FASES": "Fase 1", "CÓDIGO": "S2", "CATEGORÍA": "Cat 1",
                "NOMBRE DE SERVICIO": "Servicio test 2",
                "ENTREGABLE": "Ent B", "UND ENTREGABLE": "Und", "CANTIDAD": "1",
                "ACTIVIDADES CLAVES": "Act B",
                # Esta forzará una excepción simulada en la siguiente sección.
                "ACCIONES CLAVES": "BAD_ROW", "TIEMPO (HORAS)": "1",
            },
            {
                "FASES": "Fase 1", "CÓDIGO": "S2", "CATEGORÍA": "Cat 1",
                "NOMBRE DE SERVICIO": "Servicio test 2",
                "ENTREGABLE": "Ent B", "UND ENTREGABLE": "Und", "CANTIDAD": "1",
                "ACTIVIDADES CLAVES": "Act B",
                "ACCIONES CLAVES": "Acción ok 2", "TIEMPO (HORAS)": "1",
            },
        ])

        original_create = ServiceActivity.objects.create

        def faulty_create(*args, **kwargs):
            if kwargs.get("name") == "BAD_ROW":
                # Simula una violación de constraint persistente
                from django.db.utils import DataError
                raise DataError("simulated DB constraint failure")
            return original_create(*args, **kwargs)

        monkeypatch.setattr(ServiceActivity.objects, "create", faulty_create)

        result = import_services(wb, inactivate_missing=False)

        # La fila mala se reporta pero las dos buenas siguen vivas.
        assert ServiceActivity.objects.filter(name="Acción ok 1").exists()
        assert ServiceActivity.objects.filter(name="Acción ok 2").exists()
        assert any("BAD_ROW" in err or "simulated" in err for err in result["errors"]), result["errors"]
