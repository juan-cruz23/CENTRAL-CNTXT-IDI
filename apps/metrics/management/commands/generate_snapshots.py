"""
Management command to generate EVM metric snapshots for all active projects.

Usage:
    ./venv/bin/python manage.py generate_snapshots
    ./venv/bin/python manage.py generate_snapshots --project 3
    ./venv/bin/python manage.py generate_snapshots --all-statuses
"""

from django.core.management.base import BaseCommand

from apps.projects.models import Project
from domain.metrics.calculators import EVMCalculator


class Command(BaseCommand):
    help = "Generate EVM metric snapshots for active projects."

    def add_arguments(self, parser):
        parser.add_argument(
            "--project",
            type=int,
            help="Generate snapshot for a specific project (by PK).",
        )
        parser.add_argument(
            "--all-statuses",
            action="store_true",
            help="Generate snapshots for all projects, not just ACTIVE.",
        )

    def handle(self, *args, **options):
        if options["project"]:
            projects = Project.objects.filter(pk=options["project"])
        elif options["all_statuses"]:
            projects = Project.objects.exclude(status=Project.Status.CANCELLED)
        else:
            projects = Project.objects.filter(status=Project.Status.ACTIVE)

        total = projects.count()
        self.stdout.write(f"Generating snapshots for {total} project(s)...")

        success = 0
        for project in projects:
            try:
                calculator = EVMCalculator(project)
                snapshot = calculator.create_snapshot()

                # Update project-level metrics
                metrics = calculator.calculate()
                project.current_progress_pct = metrics["overall_progress_pct"]
                project.schedule_deviation_pct = metrics["schedule_deviation_pct"]
                project.profitability_pct = metrics["projected_margin_pct"]
                project.save(update_fields=[
                    "current_progress_pct",
                    "schedule_deviation_pct",
                    "profitability_pct",
                ])

                self.stdout.write(
                    f"  [{project.code}] SPI={snapshot.spi} CPI={snapshot.cpi} "
                    f"Progress={metrics['overall_progress_pct']}%"
                )
                success += 1
            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(f"  [{project.code}] Error: {e}")
                )

        self.stdout.write(
            self.style.SUCCESS(f"Done. {success}/{total} snapshots generated.")
        )
