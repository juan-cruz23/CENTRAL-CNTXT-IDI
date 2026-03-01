"""
Celery tasks for computing and storing EVM metric snapshots.

Scheduled tasks:
- calculate_all_metrics: runs daily to snapshot all active projects.
- detect_deviations: runs daily to flag projects with SPI or CPI below threshold.
"""

import logging
from datetime import date

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def calculate_project_metrics(self, project_id):
    """
    Calculate and store a new EVM metric snapshot for a single project.

    Args:
        project_id: Primary key of the Project to compute metrics for.

    Returns:
        dict with the snapshot id and computed metrics, or None on failure.
    """
    from apps.projects.models import Project
    from domain.metrics.calculators import EVMCalculator

    try:
        project = Project.objects.get(pk=project_id)
    except Project.DoesNotExist:
        logger.error("Project %s does not exist. Skipping metric calculation.", project_id)
        return None

    try:
        calculator = EVMCalculator(project)
        snapshot = calculator.create_snapshot(snapshot_date=date.today())
        logger.info(
            "Metric snapshot created for project '%s' (id=%s) on %s. "
            "SPI=%.4f, CPI=%.4f",
            project,
            project.pk,
            snapshot.snapshot_date,
            snapshot.spi,
            snapshot.cpi,
        )
        return {
            "snapshot_id": snapshot.pk,
            "project_id": project.pk,
            "spi": str(snapshot.spi),
            "cpi": str(snapshot.cpi),
        }
    except Exception as exc:
        logger.exception(
            "Error calculating metrics for project %s: %s", project_id, exc
        )
        raise self.retry(exc=exc)


@shared_task
def calculate_all_metrics():
    """
    Calculate EVM metric snapshots for all ACTIVE projects.

    Dispatches individual calculate_project_metrics tasks for each
    active project to enable parallel processing.
    """
    from apps.projects.models import Project

    active_projects = Project.objects.filter(status="ACTIVE")
    count = 0

    for project in active_projects.iterator():
        calculate_project_metrics.delay(project.pk)
        count += 1

    logger.info("Dispatched metric calculations for %d active projects.", count)
    return {"dispatched": count}


@shared_task
def detect_deviations():
    """
    Check the latest metric snapshot for each active project and create
    alerts when SPI or CPI falls below the threshold of 0.9.

    Alert severity:
    - SPI < 0.9: Schedule deviation alert
    - CPI < 0.9: Cost deviation alert
    - Both < 0.9: Combined deviation alert (critical)
    """
    from apps.metrics.models import ProjectMetricSnapshot
    from apps.projects.models import Project

    threshold = 0.9
    active_projects = Project.objects.filter(status="ACTIVE")
    alerts_created = 0

    for project in active_projects.iterator():
        latest_snapshot = (
            ProjectMetricSnapshot.objects.filter(project=project)
            .order_by("-snapshot_date")
            .first()
        )

        if not latest_snapshot:
            continue

        spi_below = latest_snapshot.spi < threshold
        cpi_below = latest_snapshot.cpi < threshold

        if not spi_below and not cpi_below:
            continue

        # Build alert message
        issues = []
        if spi_below:
            issues.append(
                f"SPI={latest_snapshot.spi:.4f} (umbral: {threshold})"
            )
        if cpi_below:
            issues.append(
                f"CPI={latest_snapshot.cpi:.4f} (umbral: {threshold})"
            )

        severity = "CRITICAL" if (spi_below and cpi_below) else "WARNING"
        message = (
            f"[{severity}] Desviación detectada en proyecto '{project}': "
            + ", ".join(issues)
            + f". Fecha snapshot: {latest_snapshot.snapshot_date}."
        )

        # Attempt to create a notification/alert if the Notification model exists
        try:
            from apps.notifications.models import Notification

            Notification.objects.create(
                project=project,
                notification_type="DEVIATION",
                severity=severity,
                message=message,
            )
            alerts_created += 1
        except (ImportError, Exception) as exc:
            # Notification model may not exist yet; log the alert instead
            logger.warning(
                "Could not create notification for project %s: %s. "
                "Alert message: %s",
                project.pk,
                exc,
                message,
            )
            alerts_created += 1

    logger.info(
        "Deviation detection complete. %d alerts created/logged.", alerts_created
    )
    return {"alerts_created": alerts_created}
