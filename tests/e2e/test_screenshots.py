"""
Playwright-based screenshot tests for visual regression checking.

Prerequisites:
    pip install playwright pytest-playwright
    playwright install chromium

Usage:
    pytest tests/e2e/ -v --headed  (to watch)
    pytest tests/e2e/ -v           (headless)

Screenshots are saved to tests/e2e/screenshots/
"""
import os
import pytest

try:
    from playwright.sync_api import sync_playwright
    HAS_PLAYWRIGHT = True
except ImportError:
    HAS_PLAYWRIGHT = False

pytestmark = [
    pytest.mark.skipif(not HAS_PLAYWRIGHT, reason="playwright not installed"),
    pytest.mark.e2e,
]


# ---------------------------------------------------------------------------
# URLs to screenshot
# ---------------------------------------------------------------------------
STATIC_URLS = [
    ("/", "home"),
    ("/portfolio/", "portfolio"),
    ("/mi-tablero/", "leader"),
    ("/proyectos/", "project_list"),
    ("/proyectos/crear/", "project_create"),
    ("/proyectos/clientes/", "client_list"),
    ("/proyectos/clientes/crear/", "client_create"),
    ("/servicios/categories/", "category_list"),
    ("/servicios/phases/", "phase_list"),
    ("/servicios/templates/", "servicetemplate_list"),
    ("/servicios/templates/create/", "servicetemplate_create"),
    ("/financiero/rentabilidad/", "profitability_overview"),
    ("/capacidad/", "capacity_overview"),
    ("/capacidad/heatmap/", "capacity_heatmap"),
    ("/capacidad/matriz/", "capacity_matrix"),
    ("/capacidad/alertas/", "capacity_alerts"),
    ("/capacidad/asignar/", "capacity_allocate"),
    ("/notificaciones/", "notifications_list"),
    ("/importar/", "import_wizard"),
    ("/importar/subir/", "import_upload"),
    ("/organizacion/systems/", "system_list"),
    ("/organizacion/business-units/", "businessunit_list"),
    ("/organizacion/operative-lines/", "operativeline_list"),
    ("/cuentas/profile/", "profile"),
]

# URLs that require a project pk will be formatted at runtime
PROJECT_URLS = [
    ("/proyecto/{pk}/", "project_dashboard"),
    ("/proyectos/{pk}/", "project_detail"),
    ("/proyectos/{pk}/editar/", "project_update"),
    ("/financiero/proyecto/{pk}/", "project_financial"),
    ("/financiero/proyecto/{pk}/pagos/", "payment_list"),
    ("/financiero/proyecto/{pk}/pagos/crear/", "payment_create"),
    ("/metricas/proyecto/{pk}/", "project_metrics"),
    ("/metricas/proyecto/{pk}/historial/", "metric_history"),
    ("/satisfaccion/proyecto/{pk}/", "project_satisfaction"),
    ("/satisfaccion/proyecto/{pk}/cve/crear/", "cve_create"),
    ("/satisfaccion/proyecto/{pk}/encuesta/crear/", "survey_create"),
    ("/documentos/proyecto/{pk}/", "document_list"),
    ("/documentos/proyecto/{pk}/crear/", "document_create"),
    ("/rfis/proyecto/{pk}/", "rfi_list"),
    ("/rfis/proyecto/{pk}/crear/", "rfi_create"),
]


@pytest.fixture(scope="module")
def browser_context():
    """Launch browser once for the entire module."""
    if not HAS_PLAYWRIGHT:
        pytest.skip("playwright not installed")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 720})
        yield context
        context.close()
        browser.close()


@pytest.fixture(scope="module")
def authenticated_page(browser_context, live_server):
    """Create a page, login once, and reuse for all tests."""
    page = browser_context.new_page()
    # Create admin user via Django ORM
    from django.contrib.auth import get_user_model
    User = get_user_model()
    if not User.objects.filter(username="screenshot_admin").exists():
        User.objects.create_superuser(
            username="screenshot_admin",
            password="testpass123",
            email="screenshots@test.com",
        )

    # Login
    page.goto(f"{live_server.url}/cuentas/login/")
    page.fill("input[name='username']", "screenshot_admin")
    page.fill("input[name='password']", "testpass123")
    page.click("button[type='submit'], input[type='submit']")
    page.wait_for_load_state("networkidle")

    yield page, live_server
    page.close()


@pytest.fixture(scope="module")
def test_project(live_server):
    """Create a project with associated data for project-scoped URLs."""
    from tests.factories import (
        ProjectFactory,
        ProjectPhaseInstanceFactory,
        ServiceInstanceFactory,
        MilestoneFactory,
        PaymentMilestoneFactory,
        ProjectMetricSnapshotFactory,
        SatisfactionMeasurementFactory,
    )
    proj = ProjectFactory()
    phase = ProjectPhaseInstanceFactory(project=proj)
    ServiceInstanceFactory(project=proj, phase_instance=phase)
    MilestoneFactory(project=proj)
    PaymentMilestoneFactory(project=proj)
    ProjectMetricSnapshotFactory(project=proj)
    SatisfactionMeasurementFactory(project=proj)
    return proj


@pytest.mark.parametrize("url_path,name", STATIC_URLS)
def test_screenshot_static(authenticated_page, screenshots_dir, url_path, name):
    page, live_server = authenticated_page
    page.goto(f"{live_server.url}{url_path}")
    page.wait_for_load_state("networkidle")
    screenshot_path = os.path.join(screenshots_dir, f"{name}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    assert os.path.exists(screenshot_path)


@pytest.mark.parametrize("url_template,name", PROJECT_URLS)
def test_screenshot_project(authenticated_page, screenshots_dir, test_project, url_template, name):
    page, live_server = authenticated_page
    url_path = url_template.format(pk=test_project.pk)
    page.goto(f"{live_server.url}{url_path}")
    page.wait_for_load_state("networkidle")
    screenshot_path = os.path.join(screenshots_dir, f"{name}.png")
    page.screenshot(path=screenshot_path, full_page=True)
    assert os.path.exists(screenshot_path)
