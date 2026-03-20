"""
Test suite for all new views:
1. Pricing Dashboard
2. Weekly Time Distribution Widget
3. Google Calendar Integration
4. Heatmap Drill-down
5. Role-based Access Control
"""

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import django
django.setup()

from datetime import date, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from apps.accounts.models import Role, UserRole
from apps.capacity.models import ProjectAllocation, TeamMemberCapacity
from apps.calendar_sync.models import (
    CalendarEvent,
    GoogleCalendarConnection,
    ProjectKeywordMapping,
)
from apps.projects.models import Client as ProjectClient, Project
from apps.services.models import (
    ProjectCategory,
    ProjectPhase,
    ServiceTemplate,
)
from apps.timetracking.models import TimeDistributionEntry, WeeklyTimeDistribution

User = get_user_model()


class BaseTestCase(TestCase):
    """Base test case with common setup."""

    @classmethod
    def setUpTestData(cls):
        # Admin user (full access)
        cls.admin = User.objects.create_superuser(
            username="admin_test",
            password="testpass123",
            first_name="Admin",
            last_name="Test",
        )
        # DO user (financial + pricing access)
        cls.do_user = User.objects.create_user(
            username="do_test",
            password="testpass123",
            first_name="Director",
            last_name="Operativo",
        )
        cls.role_do = Role.objects.create(code="DO", name="Dirección Operativa")
        UserRole.objects.create(user=cls.do_user, role=cls.role_do, is_primary=True)

        # LP user (operational, no financial)
        cls.lp_user = User.objects.create_user(
            username="lp_test",
            password="testpass123",
            first_name="Líder",
            last_name="Proyecto",
        )
        cls.role_lp = Role.objects.create(code="LP", name="Líder de Proyecto")
        UserRole.objects.create(user=cls.lp_user, role=cls.role_lp, is_primary=True)

        # VS user (basic, no financial, no executive)
        cls.vs_user = User.objects.create_user(
            username="vs_test",
            password="testpass123",
            first_name="Visor",
            last_name="Seguimiento",
        )
        cls.role_vs = Role.objects.create(code="VS", name="Visor de Seguimiento")
        UserRole.objects.create(user=cls.vs_user, role=cls.role_vs, is_primary=True)

        # Service data
        cls.category = ProjectCategory.objects.create(
            code="D3", name="Vivienda Campestre"
        )
        cls.phase = ProjectPhase.objects.create(number=1, name="Fase 1")
        cls.service_template = ServiceTemplate.objects.create(
            code="D3.1",
            name="Diseño Conceptual Vivienda",
            category=cls.category,
            phase=cls.phase,
            base_unit_price=Decimal("5000000"),
            estimated_hours=Decimal("40"),
            target_margin_pct=Decimal("20"),
        )
        cls.service_template_2 = ServiceTemplate.objects.create(
            code="V1.1",
            name="Pack Imágenes Urbanismo",
            category=cls.category,
            phase=cls.phase,
            base_unit_price=Decimal("3000000"),
            estimated_hours=Decimal("20"),
        )

        # Project data
        cls.client_obj = ProjectClient.objects.create(
            name="Cliente Test", category="GOLD"
        )
        cls.project = Project.objects.create(
            code="TEST-001",
            name="Proyecto Test Pontevedra",
            client=cls.client_obj,
            status="ACTIVE",
            total_value=Decimal("50000000"),
            planned_start_date=date.today() - timedelta(days=30),
            planned_end_date=date.today() + timedelta(days=60),
        )
        cls.project_2 = Project.objects.create(
            code="TEST-002",
            name="Proyecto Test Marea",
            client=cls.client_obj,
            status="ACTIVE",
            total_value=Decimal("30000000"),
            planned_start_date=date.today() - timedelta(days=15),
            planned_end_date=date.today() + timedelta(days=90),
        )

        # Capacity data
        cls.capacity = TeamMemberCapacity.objects.create(
            user=cls.do_user,
            weekly_available_hours=40,
            effective_from=date.today() - timedelta(days=90),
        )
        cls.allocation = ProjectAllocation.objects.create(
            user=cls.do_user,
            project=cls.project,
            role=cls.role_do,
            start_date=date.today() - timedelta(days=30),
            weekly_hours=20,
            allocation_pct=50,
        )

    def setUp(self):
        self.client = Client()


# ============================================================================
# 1. PRICING DASHBOARD TESTS
# ============================================================================

class PricingDashboardViewTests(BaseTestCase):

    def test_pricing_dashboard_loads(self):
        """Pricing dashboard renders correctly for admin."""
        self.client.force_login(self.admin)
        response = self.client.get("/servicios/pricing/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Pricing")
        self.assertContains(response, "Servicios Totales")

    def test_pricing_dashboard_has_kpi_data(self):
        """KPI cards show correct counts."""
        self.client.force_login(self.admin)
        response = self.client.get("/servicios/pricing/")
        self.assertContains(response, "2")  # total services

    def test_pricing_dashboard_line_filter(self):
        """Filtering by line works."""
        self.client.force_login(self.admin)
        response = self.client.get("/servicios/pricing/?linea=VIS")
        self.assertEqual(response.status_code, 200)

    def test_pricing_inline_edit_get(self):
        """Inline edit returns edit row."""
        self.client.force_login(self.admin)
        response = self.client.get(
            f"/servicios/pricing/{self.service_template.pk}/editar/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Guardar")

    def test_pricing_inline_edit_post_admin(self):
        """Admin can save inline edits."""
        self.client.force_login(self.admin)
        response = self.client.post(
            f"/servicios/pricing/{self.service_template.pk}/editar/",
            {
                "name": "Diseño Conceptual Modificado",
                "base_unit_price": "6000000",
                "estimated_hours": "45",
                "target_margin_pct": "25",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.service_template.refresh_from_db()
        self.assertEqual(self.service_template.name, "Diseño Conceptual Modificado")
        self.assertEqual(self.service_template.base_unit_price, Decimal("6000000"))

    def test_pricing_inline_edit_post_no_permission(self):
        """VS user cannot save inline edits."""
        self.client.force_login(self.vs_user)
        response = self.client.post(
            f"/servicios/pricing/{self.service_template.pk}/editar/",
            {"name": "Hacked", "base_unit_price": "0"},
        )
        self.assertEqual(response.status_code, 403)

    def test_pricing_inline_cancel(self):
        """Cancel returns display row."""
        self.client.force_login(self.admin)
        response = self.client.get(
            f"/servicios/pricing/{self.service_template.pk}/cancelar/"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.service_template.code)

    def test_pricing_do_user_can_edit(self):
        """DO user can save inline edits."""
        self.client.force_login(self.do_user)
        response = self.client.post(
            f"/servicios/pricing/{self.service_template.pk}/editar/",
            {
                "name": "Editado por DO",
                "base_unit_price": "5500000",
                "estimated_hours": "42",
                "target_margin_pct": "22",
                "is_active": "on",
            },
        )
        self.assertEqual(response.status_code, 200)


# ============================================================================
# 2. WEEKLY TIME DISTRIBUTION TESTS
# ============================================================================

class TimeDistributionWidgetTests(BaseTestCase):

    def test_widget_loads(self):
        """Widget renders for logged-in user."""
        self.client.force_login(self.do_user)
        response = self.client.get("/tiempos/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Distribución Semanal")

    def test_widget_shows_active_projects(self):
        """Widget lists active projects."""
        self.client.force_login(self.do_user)
        response = self.client.get("/tiempos/")
        self.assertContains(response, "TEST-001")
        self.assertContains(response, "TEST-002")

    def test_widget_week_navigation(self):
        """Week navigation works."""
        self.client.force_login(self.do_user)
        last_week = (date.today() - timedelta(weeks=1) - timedelta(days=date.today().weekday())).isoformat()
        response = self.client.get(f"/tiempos/?week={last_week}")
        self.assertEqual(response.status_code, 200)

    def test_save_distribution(self):
        """Saving distribution via POST."""
        self.client.force_login(self.do_user)
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()
        response = self.client.post(
            "/tiempos/guardar/",
            {
                "week_start": week_start,
                f"project_{self.project.pk}": "60",
                f"project_{self.project_2.pk}": "40",
            },
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 100)
        self.assertTrue(data["valid"])

    def test_submit_distribution(self):
        """Submitting distribution marks it as submitted."""
        self.client.force_login(self.do_user)
        today = date.today()
        week_monday = today - timedelta(days=today.weekday())
        # Use a different week to avoid conflict with other tests
        submit_week = week_monday - timedelta(weeks=3)
        week_start = submit_week.isoformat()
        response = self.client.post(
            "/tiempos/enviar/",
            {
                "week_start": week_start,
                f"project_{self.project.pk}": "70",
                f"project_{self.project_2.pk}": "30",
            },
        )
        self.assertEqual(response.status_code, 302)  # redirect
        dist = WeeklyTimeDistribution.objects.get(
            user=self.do_user,
            week_start=submit_week,
        )
        self.assertEqual(dist.status, "SUBMITTED")
        self.assertEqual(dist.entries.count(), 2)

    def test_submit_invalid_total(self):
        """Submitting with total != 100 shows error."""
        self.client.force_login(self.do_user)
        today = date.today()
        week_start = (today - timedelta(days=today.weekday())).isoformat()
        # First create the distribution
        WeeklyTimeDistribution.objects.get_or_create(
            user=self.do_user, week_start=week_start
        )
        response = self.client.post(
            "/tiempos/enviar/",
            {
                "week_start": week_start,
                f"project_{self.project.pk}": "50",
            },
            follow=True,
        )
        self.assertEqual(response.status_code, 200)
        # Check it was NOT submitted
        dist = WeeklyTimeDistribution.objects.get(
            user=self.do_user, week_start=week_start
        )
        self.assertEqual(dist.status, "DRAFT")

    def test_prefill_from_previous_week(self):
        """New week pre-fills from previous submitted week."""
        self.client.force_login(self.do_user)
        today = date.today()
        prev_week = today - timedelta(days=today.weekday()) - timedelta(weeks=1)

        # Create and submit previous week
        dist = WeeklyTimeDistribution.objects.create(
            user=self.do_user,
            week_start=prev_week,
            status="SUBMITTED",
        )
        TimeDistributionEntry.objects.create(
            distribution=dist,
            project=self.project,
            percentage=80,
        )
        TimeDistributionEntry.objects.create(
            distribution=dist,
            project=self.project_2,
            percentage=20,
        )

        # Load current week - should pre-fill
        response = self.client.get("/tiempos/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "80")  # pre-filled percentage

    def test_history_view(self):
        """History view loads."""
        self.client.force_login(self.do_user)
        response = self.client.get("/tiempos/historial/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Historial")

    def test_requires_login(self):
        """Widget requires authentication."""
        response = self.client.get("/tiempos/")
        self.assertEqual(response.status_code, 302)  # redirect to login


# ============================================================================
# 3. GOOGLE CALENDAR INTEGRATION TESTS
# ============================================================================

class CalendarSyncTests(BaseTestCase):

    def test_dashboard_loads(self):
        """Calendar dashboard renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/calendario/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Google Calendar")

    def test_dashboard_shows_setup_when_not_connected(self):
        """Shows setup instructions when not connected."""
        self.client.force_login(self.admin)
        response = self.client.get("/calendario/")
        self.assertContains(response, "Configuración Pendiente")

    def test_dashboard_shows_connected(self):
        """Shows connected badge when connected."""
        GoogleCalendarConnection.objects.create(
            user=self.admin, is_active=True
        )
        self.client.force_login(self.admin)
        response = self.client.get("/calendario/")
        self.assertContains(response, "Conectado")

    def test_event_list_loads(self):
        """Event list renders."""
        self.client.force_login(self.admin)
        response = self.client.get("/calendario/eventos/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Eventos Importados")

    def test_event_list_filters(self):
        """Event list filter works."""
        self.client.force_login(self.admin)
        response = self.client.get("/calendario/eventos/?match=unmatched")
        self.assertEqual(response.status_code, 200)

    def test_keyword_mapping_create(self):
        """Create keyword mapping."""
        self.client.force_login(self.admin)
        response = self.client.post(
            "/calendario/palabras-clave/crear/",
            {
                "keyword": "Pontevedra",
                "project_id": self.project.pk,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            ProjectKeywordMapping.objects.filter(
                keyword="Pontevedra", project=self.project
            ).exists()
        )

    def test_keyword_mapping_delete(self):
        """Delete keyword mapping."""
        km = ProjectKeywordMapping.objects.create(
            keyword="Test", project=self.project
        )
        self.client.force_login(self.admin)
        response = self.client.post(f"/calendario/palabras-clave/{km.pk}/eliminar/")
        self.assertEqual(response.status_code, 302)
        self.assertFalse(ProjectKeywordMapping.objects.filter(pk=km.pk).exists())

    def test_assign_event(self):
        """Manually assign event to project."""
        from django.utils import timezone
        event = CalendarEvent.objects.create(
            user=self.admin,
            google_event_id="evt123",
            title="Revisión diseño",
            start_time=timezone.now(),
            end_time=timezone.now() + timedelta(hours=1),
        )
        self.client.force_login(self.admin)
        response = self.client.post(
            f"/calendario/eventos/{event.pk}/asignar/",
            {"project_id": self.project.pk},
        )
        self.assertEqual(response.status_code, 200)
        event.refresh_from_db()
        self.assertEqual(event.project, self.project)
        self.assertEqual(event.match_method, "MANUAL")

    def test_event_matching_by_keyword(self):
        """Matching service finds project by keyword."""
        from apps.calendar_sync.services import match_event_to_project

        ProjectKeywordMapping.objects.create(
            keyword="pontevedra", project=self.project
        )
        project, method = match_event_to_project(
            self.admin, "Reunión Pontevedra Cliente"
        )
        self.assertEqual(project, self.project)
        self.assertEqual(method, "AUTO_NAME")

    def test_event_matching_by_project_code(self):
        """Matching service finds project by code in title."""
        from apps.calendar_sync.services import match_event_to_project

        project, method = match_event_to_project(
            self.admin, "Revisión TEST-001 Entrega"
        )
        self.assertEqual(project, self.project)
        self.assertEqual(method, "AUTO_NAME")

    def test_event_matching_unmatched(self):
        """Unmatched events return None."""
        from apps.calendar_sync.services import match_event_to_project

        project, method = match_event_to_project(
            self.admin, "Almuerzo personal"
        )
        self.assertIsNone(project)
        self.assertEqual(method, "UNMATCHED")


# ============================================================================
# 4. HEATMAP DRILL-DOWN TESTS
# ============================================================================

class HeatmapDrilldownTests(BaseTestCase):

    def test_heatmap_json_includes_user_ids(self):
        """Heatmap JSON response includes user_ids and week_dates."""
        self.client.force_login(self.admin)
        response = self.client.get(
            "/capacidad/heatmap/",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn("user_ids", data)
        self.assertIn("week_dates", data)
        if data["user_ids"]:
            self.assertIsInstance(data["user_ids"][0], int)

    def test_heatmap_template_has_modal(self):
        """Heatmap template includes drilldown modal."""
        self.client.force_login(self.admin)
        response = self.client.get("/capacidad/heatmap/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "drilldown-modal")
        self.assertContains(response, "drilldown-content")
        self.assertContains(response, "Clic para ver detalle")

    def test_drilldown_endpoint_returns_detail(self):
        """Drilldown endpoint returns user allocation details."""
        self.client.force_login(self.admin)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        response = self.client.get(
            f"/capacidad/heatmap/detalle/?user_id={self.do_user.pk}&week={week_start.isoformat()}"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Director Operativo")
        self.assertContains(response, "TEST-001")
        self.assertContains(response, "20h")

    def test_drilldown_shows_utilization(self):
        """Drilldown shows utilization percentage."""
        self.client.force_login(self.admin)
        today = date.today()
        week_start = today - timedelta(days=today.weekday())
        response = self.client.get(
            f"/capacidad/heatmap/detalle/?user_id={self.do_user.pk}&week={week_start.isoformat()}"
        )
        self.assertContains(response, "50%")  # 20h/40h = 50%

    def test_drilldown_missing_params(self):
        """Drilldown with missing params returns empty."""
        self.client.force_login(self.admin)
        response = self.client.get("/capacidad/heatmap/detalle/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_drilldown_invalid_user(self):
        """Drilldown with invalid user returns empty."""
        self.client.force_login(self.admin)
        response = self.client.get(
            "/capacidad/heatmap/detalle/?user_id=99999&week=2026-03-16"
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content, b"")

    def test_drilldown_empty_week(self):
        """Drilldown for a week with no allocations shows message."""
        self.client.force_login(self.admin)
        # Use a far future date
        response = self.client.get(
            f"/capacidad/heatmap/detalle/?user_id={self.vs_user.pk}&week=2027-01-04"
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No hay asignaciones")


# ============================================================================
# 5. ROLE-BASED ACCESS CONTROL TESTS
# ============================================================================

class RoleBasedAccessTests(BaseTestCase):

    # --- Financial views ---

    def test_admin_can_access_profitability(self):
        """Admin can access profitability view."""
        self.client.force_login(self.admin)
        response = self.client.get("/financiero/rentabilidad/")
        self.assertEqual(response.status_code, 200)

    def test_do_user_can_access_profitability(self):
        """DO user can access profitability view."""
        self.client.force_login(self.do_user)
        response = self.client.get("/financiero/rentabilidad/")
        self.assertEqual(response.status_code, 200)

    def test_lp_user_cannot_access_profitability(self):
        """LP user cannot access profitability view."""
        self.client.force_login(self.lp_user)
        response = self.client.get("/financiero/rentabilidad/")
        self.assertEqual(response.status_code, 403)

    def test_vs_user_cannot_access_profitability(self):
        """VS user cannot access profitability view."""
        self.client.force_login(self.vs_user)
        response = self.client.get("/financiero/rentabilidad/")
        self.assertEqual(response.status_code, 403)

    def test_vs_user_cannot_access_accounting(self):
        """VS user cannot access accounting view."""
        self.client.force_login(self.vs_user)
        response = self.client.get("/financiero/contabilidad/")
        self.assertEqual(response.status_code, 403)

    def test_vs_user_cannot_access_cost_centers(self):
        """VS user cannot access cost center mapping."""
        self.client.force_login(self.vs_user)
        response = self.client.get("/financiero/centros-costo/")
        self.assertEqual(response.status_code, 403)

    def test_vs_user_cannot_access_cost_allocation(self):
        """VS user cannot access cost allocation."""
        self.client.force_login(self.vs_user)
        response = self.client.get("/financiero/prorrateo/")
        self.assertEqual(response.status_code, 403)

    # --- Sidebar visibility ---

    def test_admin_sidebar_shows_financials(self):
        """Admin sees financial section in sidebar."""
        self.client.force_login(self.admin)
        response = self.client.get("/")
        self.assertContains(response, "Rentabilidad")
        self.assertContains(response, "Contabilidad")
        self.assertContains(response, "Pricing")

    def test_vs_sidebar_hides_financials(self):
        """VS user does not see financial section in sidebar."""
        self.client.force_login(self.vs_user)
        response = self.client.get("/")
        self.assertNotContains(response, "Rentabilidad")
        self.assertNotContains(response, "Contabilidad")
        self.assertNotContains(response, "Pricing")

    def test_do_sidebar_shows_financials(self):
        """DO user sees financial section in sidebar."""
        self.client.force_login(self.do_user)
        response = self.client.get("/")
        self.assertContains(response, "Rentabilidad")
        self.assertContains(response, "Pricing")

    # --- Pricing edit permissions ---

    def test_pricing_edit_button_visible_for_do(self):
        """DO user sees edit buttons in pricing dashboard."""
        self.client.force_login(self.do_user)
        response = self.client.get("/servicios/pricing/")
        self.assertContains(response, "Editar")

    def test_pricing_edit_button_hidden_for_lp(self):
        """LP user does not see edit buttons in pricing dashboard."""
        self.client.force_login(self.lp_user)
        response = self.client.get("/servicios/pricing/")
        self.assertNotContains(response, "pricing_inline_edit")  # no inline edit buttons

    # --- Unauthenticated access ---

    def test_unauthenticated_redirects(self):
        """Unauthenticated user is redirected."""
        urls = [
            "/servicios/pricing/",
            "/tiempos/",
            "/calendario/",
            "/capacidad/heatmap/",
            "/financiero/rentabilidad/",
        ]
        for url in urls:
            response = self.client.get(url)
            self.assertEqual(
                response.status_code, 302,
                f"{url} should redirect unauthenticated users",
            )

    # --- Context processor ---

    def test_context_processor_admin(self):
        """Admin gets all permission flags True."""
        self.client.force_login(self.admin)
        response = self.client.get("/")
        self.assertTrue(response.context.get("can_view_financials"))
        self.assertTrue(response.context.get("can_edit_pricing"))
        self.assertTrue(response.context.get("can_view_executive"))
        self.assertTrue(response.context.get("can_view_operations"))

    def test_context_processor_vs(self):
        """VS user gets no financial/pricing flags."""
        self.client.force_login(self.vs_user)
        response = self.client.get("/")
        self.assertFalse(response.context.get("can_view_financials"))
        self.assertFalse(response.context.get("can_edit_pricing"))
        self.assertFalse(response.context.get("can_view_executive"))
        self.assertFalse(response.context.get("can_view_operations"))

    def test_context_processor_do(self):
        """DO user gets financial + pricing flags."""
        self.client.force_login(self.do_user)
        response = self.client.get("/")
        self.assertTrue(response.context.get("can_view_financials"))
        self.assertTrue(response.context.get("can_edit_pricing"))
        self.assertTrue(response.context.get("can_view_executive"))
        self.assertTrue(response.context.get("can_view_operations"))


# ============================================================================
# Run
# ============================================================================

if __name__ == "__main__":
    import unittest
    unittest.main()
