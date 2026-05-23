"""Tests para las 7 mejoras del PDF cliente CNTXT en issue #21.

Cada test mapea 1:1 con una nota:
- Nota 1: SubCategoria con múltiples líneas operativas (M2M)
- Nota 3: ProjectPhase delete con manejo de error
- Nota 4: ThirdPartyDeleteView (solo staff/superuser)
- Nota 5: Project.code editable manual en edición
- Nota 8: UX contactos — link visible al admin
- Nota 11: cronograma colapsable por fase (smoke template render)
- Nota 12: Milestone manual asociado a fase + segregación
"""

from datetime import date

import pytest
from django.urls import reverse


# ---------------------------------------------------------------------------
# Nota 1: SubCategoria con múltiples líneas operativas
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_nota1_servicesubcategory_acepta_multiples_lineas_operativas():
    """ServiceSubCategory ahora soporta M2M operative_lines; debe poder
    asignarse a varias líneas a la vez."""
    from apps.services.models import ServiceSubCategory
    from tests.factories.organizations import OperativeLineFactory

    sub = ServiceSubCategory.objects.create(code="ZZ", name="Cross-line")
    line_a = OperativeLineFactory()
    line_b = OperativeLineFactory()
    line_c = OperativeLineFactory()
    sub.operative_lines.set([line_a, line_b, line_c])

    sub.refresh_from_db()
    assert sub.operative_lines.count() == 3
    assert set(sub.operative_lines.values_list("pk", flat=True)) == {
        line_a.pk, line_b.pk, line_c.pk,
    }


@pytest.mark.django_db
def test_nota1_form_subcategoria_acepta_multiselect():
    """El form de subcategoría acepta múltiples líneas via SelectMultiple."""
    from apps.services.forms import ServiceSubCategoryForm
    from tests.factories.organizations import OperativeLineFactory

    line_a = OperativeLineFactory()
    line_b = OperativeLineFactory()
    form = ServiceSubCategoryForm(data={
        "code": "AA",
        "name": "Multi",
        "operative_lines": [str(line_a.pk), str(line_b.pk)],
        "description": "",
        "is_active": True,
    })
    assert form.is_valid(), form.errors
    sub = form.save()
    assert sub.operative_lines.count() == 2


# ---------------------------------------------------------------------------
# Nota 3: ProjectPhase delete con manejo de error
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_nota3_delete_phase_devuelve_redirect_no_500(admin_client):
    """La vista de eliminar fase NO debe responder 500 ante error de cascada
    o validación. Debe redirigir al list con `messages.error` o success."""
    from tests.factories.services import ProjectPhaseFactory

    phase = ProjectPhaseFactory()
    url = reverse("services:phase_delete", kwargs={"pk": phase.pk})
    # GET debe renderizar confirmación
    resp = admin_client.get(url)
    assert resp.status_code == 200
    # POST debe redirigir (302) no crashear
    resp = admin_client.post(url)
    assert resp.status_code in (302, 200), f"esperaba redirect, obtuve {resp.status_code}"


# ---------------------------------------------------------------------------
# Nota 4: ThirdPartyDeleteView solo staff/superuser
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_nota4_eliminar_tercero_url_existe():
    """La URL `terceros:delete` debe existir y resolver correctamente."""
    url = reverse("terceros:delete", kwargs={"pk": 1})
    assert "/terceros/" in url
    assert "/eliminar/" in url


@pytest.mark.django_db
def test_nota4_usuario_normal_no_puede_eliminar_tercero(authenticated_client):
    """Un usuario sin is_staff NO debe poder acceder a la vista de delete."""
    from apps.terceros.models import ThirdParty
    tp = ThirdParty.objects.create(
        name="Test Cliente",
        relationship_type=ThirdParty.RelationshipType.CLIENTE,
    )
    url = reverse("terceros:delete", kwargs={"pk": tp.pk})
    resp = authenticated_client.get(url)
    # UserPassesTestMixin sin login_url devuelve 403
    assert resp.status_code == 403, f"esperaba 403, obtuve {resp.status_code}"
    assert ThirdParty.objects.filter(pk=tp.pk).exists()


@pytest.mark.django_db
def test_nota4_staff_puede_eliminar_tercero_sin_proyectos(admin_client):
    """Staff puede eliminar un tercero que NO tenga proyectos asociados."""
    from apps.terceros.models import ThirdParty
    tp = ThirdParty.objects.create(
        name="Tercero Prueba",
        relationship_type=ThirdParty.RelationshipType.PROSPECTO,
    )
    url = reverse("terceros:delete", kwargs={"pk": tp.pk})
    resp = admin_client.post(url)
    assert resp.status_code == 302
    assert not ThirdParty.objects.filter(pk=tp.pk).exists()


# ---------------------------------------------------------------------------
# Nota 5: Project.code editable en edición
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_nota5_project_form_code_oculto_en_create():
    """En creación, el campo `code` se autogenera y NO se renderiza."""
    from apps.projects.forms import ProjectForm
    form = ProjectForm()
    assert "code" not in form.fields


@pytest.mark.django_db
def test_nota5_project_form_code_editable_en_update():
    """En edición, el campo `code` DEBE estar disponible y editable."""
    from apps.projects.forms import ProjectForm
    from tests.factories.projects import ProjectFactory
    project = ProjectFactory(code="216")
    form = ProjectForm(instance=project)
    assert "code" in form.fields, "code debe ser editable en modo edición"
    assert form.fields["code"].help_text  # tiene help text


# ---------------------------------------------------------------------------
# Nota 8: link a admin para editar contactos
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_nota8_detalle_tercero_muestra_link_editar_contactos(authenticated_client):
    """La vista detalle de tercero debe incluir un link visible a admin
    para editar contactos."""
    from apps.terceros.models import ThirdParty
    tp = ThirdParty.objects.create(
        name="Cliente Demo",
        relationship_type=ThirdParty.RelationshipType.CLIENTE,
    )
    resp = authenticated_client.get(
        reverse("terceros:detail", kwargs={"pk": tp.pk})
    )
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "Editar contactos" in content
    assert "/admin/terceros/thirdpartycontact/" in content


# ---------------------------------------------------------------------------
# Nota 11 + 12: cronograma agrupado y colapsable, con hitos por fase
# ---------------------------------------------------------------------------
@pytest.mark.django_db
def test_nota11_schedule_table_view_renderiza_phase_groups(authenticated_client):
    """ScheduleTableView debe construir phase_groups con services y milestones."""
    from tests.factories.projects import ProjectFactory
    project = ProjectFactory()
    resp = authenticated_client.get(
        reverse("projects:schedule_table", kwargs={"pk": project.pk})
    )
    assert resp.status_code == 200
    # Sin datos: muestra empty state
    assert b"Sin servicios en el cronograma" in resp.content or b"hito" in resp.content.lower()


@pytest.mark.django_db
def test_nota12_milestone_create_modal_acepta_phase_instance(authenticated_client):
    """MilestoneCreateView POST con phase_instance debe asociar el hito a la fase."""
    from apps.projects.models import Milestone
    from tests.factories.projects import ProjectFactory, ProjectPhaseInstanceFactory

    project = ProjectFactory()
    pi = ProjectPhaseInstanceFactory(project=project)

    url = reverse("projects:milestone_create", kwargs={"pk": project.pk})
    resp = authenticated_client.post(url, data={
        "milestone_type": "CLIENT_REVIEW",
        "code": "R1",
        "name": "Revisión Cliente Fase 1",
        "phase_instance": str(pi.pk),
        "planned_date": "2026-06-15",
    })
    # El modal flow devuelve HttpResponse vacío con HX-Trigger
    assert resp.status_code == 200
    assert resp.get("HX-Trigger") == "scheduleChanged"

    m = Milestone.objects.get(project=project, code="R1")
    assert m.phase_instance_id == pi.pk
    assert m.milestone_type == "CLIENT_REVIEW"


@pytest.mark.django_db
def test_nota12_schedule_table_segrega_hitos_por_fase(authenticated_client):
    """ScheduleTableView debe agrupar hitos manuales bajo la fase correcta."""
    from apps.projects.models import Milestone
    from tests.factories.projects import ProjectFactory, ProjectPhaseInstanceFactory

    project = ProjectFactory()
    pi = ProjectPhaseInstanceFactory(project=project)

    Milestone.objects.create(
        project=project,
        phase_instance=pi,
        code="H1",
        name="Kickoff Fase 1",
        milestone_type=Milestone.MilestoneType.KICKOFF,
        planned_date=date(2026, 6, 1),
    )
    resp = authenticated_client.get(
        reverse("projects:schedule_table", kwargs={"pk": project.pk})
    )
    assert resp.status_code == 200
    content = resp.content.decode("utf-8")
    assert "H1" in content
    assert "Kickoff Fase 1" in content


@pytest.mark.django_db
def test_nota12_milestone_legacy_get_sigue_funcionando(authenticated_client):
    """El flow legacy ?legacy=1 sigue renderizando el partial fila para no
    romper otras vistas (project_detail tab Hitos, etc.)."""
    from tests.factories.projects import ProjectFactory
    project = ProjectFactory()
    url = reverse("projects:milestone_create", kwargs={"pk": project.pk})
    resp = authenticated_client.get(url + "?legacy=1")
    assert resp.status_code == 200
    assert b"milestone-form-row" in resp.content
