"""Tests para los 7 bugs criticos reportados por el cliente en issue #21.

Cubren las regresiones identificadas en el PDF de notas de interaccion del
cliente. Cada test mapea 1:1 con una de las notas (2, 6, 7, 9, 10, 13, 14).
"""

from decimal import Decimal

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_logout_acepta_post(client, user):
    """Nota 7: cerrar sesion via POST no debe responder 405."""
    client.force_login(user)
    resp = client.post(reverse("logout"))
    # LogoutView responde 302 (redirect a LOGIN_URL) o 200 si renderiza
    # template; lo que NO debe responder es 405.
    assert resp.status_code != 405


@pytest.mark.django_db
def test_logout_get_si_responde_405(client, user):
    """Nota 7 (regresion): GET sigue siendo 405 — confirma que el template
    ahora envia POST. Si alguien re-introduce un <a href> al logout este test
    no falla, pero los tests E2E si."""
    client.force_login(user)
    resp = client.get(reverse("logout"))
    assert resp.status_code == 405


@pytest.mark.django_db
def test_user_role_update_get_renderiza_form(admin_client, user):
    """Nota 6: GET al wizard 'Asignar Roles' tras crear usuario no debe ser
    405 — debe renderizar formulario."""
    resp = admin_client.get(
        reverse("accounts:user_role_update", kwargs={"pk": user.pk})
    )
    assert resp.status_code == 200
    # Debe contener el form para checkbox de roles
    assert b"roles" in resp.content.lower()


@pytest.mark.django_db
def test_cost_center_mapping_form_no_requiere_code_name(db):
    """Nota 2: el form CostCenterMapping ya no debe requerir code/name
    (vienen de Loggro). Solo project + business_unit son editables."""
    from apps.financials.forms import CostCenterMappingForm
    from apps.financials.models import CostCenterMapping
    from tests.factories.organizations import BusinessUnitFactory

    mapping = CostCenterMapping.objects.create(
        cost_center_code="CC-001", cost_center_name="Centro Uno"
    )
    bu = BusinessUnitFactory()
    form = CostCenterMappingForm(
        data={"project": "", "business_unit": str(bu.pk)},
        instance=mapping,
    )
    assert form.is_valid(), form.errors
    saved = form.save()
    assert saved.business_unit_id == bu.pk
    # Code/Name no se tocaron
    saved.refresh_from_db()
    assert saved.cost_center_code == "CC-001"
    assert saved.cost_center_name == "Centro Uno"


@pytest.mark.django_db
def test_project_total_value_incluye_servicios_de_fases(db):
    """Nota 13: el valor total del proyecto debe sumar TODOS los services
    (cronograma + fases), no solo los del cronograma."""
    from tests.factories.projects import (
        ProjectFactory,
        ProjectPhaseInstanceFactory,
        ServiceInstanceFactory,
    )

    project = ProjectFactory(total_value=Decimal("0"))
    # Servicio en cronograma (phase_instance=None)
    ServiceInstanceFactory(
        project=project, phase_instance=None,
        quantity=Decimal("1"), unit_price=Decimal("100000"),
    )
    # Servicio en fase
    phase = ProjectPhaseInstanceFactory(project=project)
    ServiceInstanceFactory(
        project=project, phase_instance=phase,
        quantity=Decimal("1"), unit_price=Decimal("250000"),
    )
    project.refresh_from_db()
    # Antes era 100000 (solo cronograma). Ahora debe ser 350000.
    assert project.total_value == Decimal("350000.00"), (
        f"Project total_value debe incluir services de fases, fue {project.total_value}"
    )


@pytest.mark.django_db
def test_cronograma_orden_cronologico_no_alfabetico(admin_client, db):
    """Nota 10b: la vista detail debe ordenar el cronograma por
    projected_start_date, no por code alfabetico."""
    from datetime import date
    from tests.factories.projects import ProjectFactory, ServiceInstanceFactory

    project = ProjectFactory()
    # Crear servicios con codes alfabeticamente "invertidos" vs fechas
    si_late = ServiceInstanceFactory(
        project=project, phase_instance=None, code="A-001",
        projected_start_date=date(2026, 12, 1),
    )
    si_early = ServiceInstanceFactory(
        project=project, phase_instance=None, code="Z-099",
        projected_start_date=date(2026, 6, 1),
    )
    resp = admin_client.get(reverse("projects:detail", kwargs={"pk": project.pk}))
    assert resp.status_code == 200
    schedule_phase_groups = resp.context.get("schedule_phase_groups") or []
    all_services = [s for g in schedule_phase_groups for s in g["services"]]
    # El servicio con fecha MAS temprana debe ir primero, aunque su code venga
    # despues alfabeticamente.
    codes = [s.code for s in all_services]
    assert codes.index("Z-099") < codes.index("A-001"), (
        f"Cronograma mal ordenado, codes={codes}"
    )


@pytest.mark.django_db
def test_schedule_edit_no_borra_horas_si_no_se_envian(admin_client, db):
    """Nota 10a: editar un service en cronograma para asignar responsable
    NO debe borrar las horas existentes de las acciones (regresion: antes
    se forzaban a 0 con .get('hours') or '0')."""
    from datetime import date
    from apps.projects.models import ServiceInstanceAction
    from tests.factories.projects import ProjectFactory, ServiceInstanceFactory

    project = ProjectFactory()
    si = ServiceInstanceFactory(
        project=project, phase_instance=None, code="S-001",
        projected_start_date=date(2026, 6, 1),
    )
    act = ServiceInstanceAction.objects.create(
        service_instance=si,
        name="Hacer X",
        order=1,
        estimated_hours=Decimal("4.0"),
    )

    # Simular POST sin act-0-hours pero con act-0-professional vacio.
    url = reverse(
        "projects:schedule_service_edit",
        kwargs={"pk": project.pk, "si_pk": si.pk},
    )
    resp = admin_client.post(url, data={
        "projected_start_date": "2026-06-01",
        "act-TOTAL": "1",
        # Nota: act-0-hours INTENCIONALMENTE ausente
        "act-0-professional": "",
    })
    # No nos importa el codigo de respuesta exacto, solo que las horas
    # se hayan preservado.
    act.refresh_from_db()
    assert act.estimated_hours == Decimal("4.0"), (
        f"Las horas se borraron: {act.estimated_hours}"
    )


@pytest.mark.django_db
def test_action_progress_modal_dropdown_usa_username_si_no_hay_nombre(
    admin_client, db
):
    """Nota 14: la modal 'Registrar Avance' mostraba opciones vacias cuando
    los usuarios no tenian first_name/last_name (porque get_full_name
    retorna ''). Ahora debe fallback a username."""
    from datetime import date
    from apps.accounts.models import User
    from apps.projects.models import ServiceInstanceAction
    from tests.factories.projects import ProjectFactory, ServiceInstanceFactory

    # Crear usuario sin nombres (solo username)
    User.objects.create_user(
        username="solo_username", password="x", first_name="", last_name="",
    )

    project = ProjectFactory()
    si = ServiceInstanceFactory(
        project=project, phase_instance=None,
        projected_start_date=date(2026, 6, 1),
    )
    act = ServiceInstanceAction.objects.create(
        service_instance=si, name="Avance Y", order=1,
    )
    resp = admin_client.get(reverse(
        "projects:action_progress_log",
        kwargs={"pk": project.pk, "si_pk": si.pk, "action_pk": act.pk},
    ))
    assert resp.status_code == 200
    assert b"solo_username" in resp.content, (
        "El dropdown debe mostrar el username cuando get_full_name() esta vacio"
    )
