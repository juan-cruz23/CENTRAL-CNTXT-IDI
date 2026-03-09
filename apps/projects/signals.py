"""
Signals for automatic progress roll-up.

Signal 1: ServiceInstance post_save → recalculates PhaseInstance.progress_pct
Signal 2: ProjectPhaseInstance post_save → recalculates Project.current_progress_pct

Both use weighted-average formulas based on total_value.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.db.models.signals import post_save
from django.dispatch import receiver

ZERO = Decimal("0")


@receiver(post_save, sender="projects.ServiceInstance")
def rollup_phase_progress(sender, instance, **kwargs):
    """Recalculate the parent PhaseInstance progress when a SI is saved."""
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "progress_pct" not in update_fields:
        return

    phase_instance = instance.phase_instance
    siblings = phase_instance.service_instances.all()

    total_weighted = ZERO
    total_value = ZERO

    for si in siblings:
        si_value = Decimal(str(si.total_value or 0))
        si_progress = Decimal(str(si.progress_pct or 0))
        total_weighted += si_value * si_progress
        total_value += si_value

    if total_value > ZERO:
        new_progress = (total_weighted / total_value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        new_progress = ZERO

    if phase_instance.progress_pct != new_progress:
        phase_instance.progress_pct = new_progress
        phase_instance.save(update_fields=["progress_pct", "updated_at"])


@receiver(post_save, sender="projects.ProjectPhaseInstance")
def rollup_project_progress(sender, instance, **kwargs):
    """Recalculate the parent Project progress when a PhaseInstance is saved."""
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "progress_pct" not in update_fields:
        return

    project = instance.project
    phases = project.phase_instances.all()

    total_weighted = ZERO
    total_value = ZERO

    for pi in phases:
        pi_value = Decimal(str(pi.total_value or 0))
        pi_progress = Decimal(str(pi.progress_pct or 0))
        total_weighted += pi_value * pi_progress
        total_value += pi_value

    if total_value > ZERO:
        new_progress = (total_weighted / total_value).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        new_progress = ZERO

    if project.current_progress_pct != new_progress:
        project.current_progress_pct = new_progress
        project.save(update_fields=["current_progress_pct", "updated_at"])
