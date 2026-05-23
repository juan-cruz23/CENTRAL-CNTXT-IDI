"""
Signals for automatic progress roll-up.

Signal 1: ServiceInstance post_save → recalculates PhaseInstance.progress_pct
Signal 2: ProjectPhaseInstance post_save → recalculates Project.current_progress_pct

Both use weighted-average formulas based on total_value.
"""

from decimal import ROUND_HALF_UP, Decimal

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver


@receiver(post_save, sender="projects.Project")
def auto_assign_cost_center(sender, instance, **kwargs):
    """Assign cost center based on business_unit when project is saved."""
    if not instance.business_unit_id:
        return
    from apps.financials.models import CostCenterMapping
    cc = CostCenterMapping.objects.filter(
        business_unit_id=instance.business_unit_id
    ).first()
    if cc and instance.cost_center_id != cc.pk:
        sender.objects.filter(pk=instance.pk).update(cost_center=cc)

ZERO = Decimal("0")


@receiver(post_save, sender="projects.ServiceInstance")
def rollup_phase_progress(sender, instance, **kwargs):
    """Recalculate the parent PhaseInstance progress when a SI is saved."""
    update_fields = kwargs.get("update_fields")
    if update_fields is not None and "progress_pct" not in update_fields:
        return

    phase_instance = instance.phase_instance
    if phase_instance is None:
        return
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


def _update_project_schedule_dates(project):
    """
    Recalculate planned/actual dates, total_value y avance global del Project.

    El total_value del proyecto suma TODOS los ServiceInstance (cronograma +
    fases), porque el valor del proyecto debe reflejar todo lo cobrable.
    Las fechas/horas/avance siguen tomándose del cronograma (phase_instance
    null) que es donde el equipo programa el trabajo real.
    """
    from django.db.models import Max, Min, Sum

    qs = project.service_instances.filter(phase_instance__isnull=True)
    all_si_qs = project.service_instances.all()
    agg = qs.aggregate(
        min_planned=Min("projected_start_date"),
        max_planned=Max("projected_end_date"),
        min_actual=Min("actual_start_date"),
        max_actual=Max("actual_end_date"),
        sum_projected_hours=Sum("projected_hours"),
        sum_actual_hours=Sum("actual_hours"),
    )
    total_agg = all_si_qs.aggregate(total=Sum("total_value"))
    agg["total"] = total_agg["total"]
    update_fields = []
    for model_field, agg_key in (
        ("planned_start_date", "min_planned"),
        ("planned_end_date", "max_planned"),
        ("actual_start_date", "min_actual"),
        ("actual_end_date", "max_actual"),
    ):
        new_val = agg[agg_key]
        if getattr(project, model_field) != new_val:
            setattr(project, model_field, new_val)
            update_fields.append(model_field)

    new_total = agg["total"] or ZERO
    if project.total_value != new_total:
        project.total_value = new_total
        update_fields.append("total_value")

    # Avance global ponderado por valor de cada servicio del cronograma
    total_weighted = ZERO
    total_for_progress = ZERO
    for si in qs:
        si_value = Decimal(str(si.total_value or 0))
        si_progress = Decimal(str(si.progress_pct or 0))
        total_weighted += si_value * si_progress
        total_for_progress += si_value
    if total_for_progress > ZERO:
        new_progress = (total_weighted / total_for_progress).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        new_progress = ZERO
    if project.current_progress_pct != new_progress:
        project.current_progress_pct = new_progress
        update_fields.append("current_progress_pct")

    # Desviación por horas: (Σ reales - Σ planeadas) / Σ planeadas × 100
    sum_proj = Decimal(str(agg["sum_projected_hours"] or 0))
    sum_act = Decimal(str(agg["sum_actual_hours"] or 0))
    if sum_proj > ZERO:
        new_dev = ((sum_act - sum_proj) / sum_proj * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
    else:
        new_dev = ZERO
    if project.schedule_deviation_pct != new_dev:
        project.schedule_deviation_pct = new_dev
        update_fields.append("schedule_deviation_pct")

    if update_fields:
        project.save(update_fields=update_fields + ["updated_at"])


@receiver(post_save, sender="projects.ServiceInstance")
def sync_schedule_dates_on_save(sender, instance, **kwargs):
    """Refresca métricas del proyecto al guardar cualquier ServiceInstance.

    Antes solo se disparaba para servicios del cronograma (phase_instance=None),
    pero el total_value del proyecto debe reflejar también los services en
    fases. Ahora se recalcula siempre (la función internamente diferencia
    qué métricas vienen de cronograma vs total).
    """
    _update_project_schedule_dates(instance.project)


@receiver(post_delete, sender="projects.ServiceInstance")
def sync_schedule_dates_on_delete(sender, instance, **kwargs):
    """Refresca métricas del proyecto al borrar cualquier ServiceInstance."""
    _update_project_schedule_dates(instance.project)


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
