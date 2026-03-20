"""
Script to fill missing data (services, milestones, phases) for all projects.
Based on patterns from well-populated projects (3, 4, 5, 6).

Run with:
    ./venv/bin/python manage.py shell < scripts/fill_project_data.py
"""

import os
import sys
from datetime import date, timedelta
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model

from apps.projects.models import (
    Milestone,
    Project,
    ProjectPhaseInstance,
    ServiceInstance,
)
from apps.services.models import ProjectPhase, ServiceTemplate

User = get_user_model()

# ----- Lookups -----
PHASES = {ph.number: ph for ph in ProjectPhase.objects.all()}
# phase_number -> ServiceTemplate mapping
SVC_TEMPLATES = {}
for st in ServiceTemplate.objects.all():
    SVC_TEMPLATES[st.code] = st

# Convenience: phase -> default service template
PHASE_SVC = {
    1: SVC_TEMPLATES["ARQ-INV-01"],   # Levantamiento Arquitectónico
    2: SVC_TEMPLATES["ARQ-CON-01"],   # Concepto Arquitectónico
    3: SVC_TEMPLATES["INT-ESQ-01"],   # Diseño Esquemático Interior
    4: SVC_TEMPLATES["ARQ-DES-01"],   # Desarrollo de Diseño Arquitectónico
    6: SVC_TEMPLATES["VIS-REN-01"],   # Paquete de Renders
}
SVC_RECORRIDO = SVC_TEMPLATES["VIS-REC-01"]  # Recorrido Virtual 360

# Professionals
PROS = {u.id: u for u in User.objects.exclude(id=1)}  # exclude admin
PRO_CAROLINA = User.objects.get(first_name="Carolina")     # id=2
PRO_SANTIAGO = User.objects.get(first_name="Santiago")      # id=3
PRO_VALENTINA = User.objects.get(first_name="Valentina")    # id=4
PRO_JUANPABLO = User.objects.get(first_name="Juan Pablo")   # id=5
PRO_CAMILA = User.objects.get(first_name="Camila")          # id=6
PRO_ANDRES = User.objects.get(first_name="Andrés")          # id=7

# Assign professionals to projects for variety
PRO_ASSIGNMENTS = {
    1:  (PRO_CAROLINA, PRO_JUANPABLO),   # lead, viz
    2:  (PRO_SANTIAGO, PRO_CAMILA),
    5:  (PRO_JUANPABLO, PRO_JUANPABLO),
    6:  (PRO_CAROLINA, PRO_JUANPABLO),   # already assigned
    7:  (PRO_VALENTINA, PRO_CAMILA),
    8:  (PRO_ANDRES, PRO_JUANPABLO),
    9:  (PRO_VALENTINA, PRO_CAMILA),
    10: (PRO_SANTIAGO, PRO_JUANPABLO),
    11: (PRO_CAMILA, PRO_JUANPABLO),
    12: (PRO_ANDRES, PRO_JUANPABLO),
    13: (PRO_CAROLINA, PRO_CAMILA),
    14: (PRO_VALENTINA, PRO_ANDRES),
    15: (PRO_SANTIAGO, PRO_JUANPABLO),
    16: (PRO_ANDRES, PRO_CAMILA),
    17: (PRO_SANTIAGO, PRO_JUANPABLO),
    18: (PRO_CAROLINA, PRO_JUANPABLO),
    19: (PRO_CAMILA, PRO_ANDRES),
}


def get_or_create_phase(project, phase_num):
    """Get or create a ProjectPhaseInstance for a project."""
    phase_template = PHASES[phase_num]
    pi, created = ProjectPhaseInstance.objects.get_or_create(
        project=project,
        phase=phase_template,
        defaults={"order": phase_num, "total_value": 0, "progress_pct": 0},
    )
    if created:
        print("  Created phase #%d for project %d" % (phase_num, project.id))
    return pi


def create_service(project, phase_instance, svc_template, value, progress,
                   professional=None, proj_start=None, proj_end=None):
    """Create a ServiceInstance if it doesn't already exist."""
    existing = ServiceInstance.objects.filter(
        project=project,
        phase_instance=phase_instance,
        service_template=svc_template,
    ).first()
    if existing:
        return existing

    svc_num = ServiceInstance.objects.filter(project=project).count() + 1
    code = "%s-S%02d" % (project.code, svc_num)

    svc = ServiceInstance(
        project=project,
        phase_instance=phase_instance,
        service_template=svc_template,
        code=code,
        name=svc_template.name,
        quantity=Decimal("1"),
        unit_price=Decimal(str(value)),
        # total_value computed by save()
        progress_pct=Decimal(str(progress)),
        expected_progress_pct=Decimal(str(progress)),
        assigned_professional=professional,
        projected_start_date=proj_start,
        projected_end_date=proj_end,
        projected_hours=Decimal(str(max(20, value / 200000))),
    )
    svc.save()
    print("  Created service: %s (%s) val=%s prog=%s%%" % (
        svc.name, code, value, progress))
    return svc


def create_milestone(project, ms_type, name, code, planned, actual=None, phase_instance=None):
    """Create a milestone if it doesn't already exist for this project+type+name."""
    existing = Milestone.objects.filter(
        project=project,
        milestone_type=ms_type,
        name=name,
    ).first()
    if existing:
        return existing

    ms = Milestone.objects.create(
        project=project,
        phase_instance=phase_instance,
        milestone_type=ms_type,
        name=name,
        code=code,
        planned_date=planned,
        actual_date=actual,
    )
    print("  Created milestone: %s (%s) planned=%s actual=%s" % (
        name, ms_type, planned, actual))
    return ms


def distribute_dates(start, end, num_phases):
    """Distribute start/end into num_phases equal segments."""
    if not start or not end:
        return [(None, None)] * num_phases
    total_days = (end - start).days
    segment = total_days // num_phases
    result = []
    for i in range(num_phases):
        s = start + timedelta(days=i * segment)
        e = start + timedelta(days=(i + 1) * segment - 1) if i < num_phases - 1 else end
        result.append((s, e))
    return result


def fill_full_project(project, phase_values, phase_progress, include_recorrido=False):
    """Fill a full design project with phases 1-6 (or subset) and services."""
    lead_pro, viz_pro = PRO_ASSIGNMENTS.get(project.id, (None, None))

    # Determine date segments
    active_phases = [pn for pn in sorted(phase_values.keys())]
    dates = distribute_dates(
        project.planned_start_date, project.planned_end_date, len(active_phases)
    )

    for idx, phase_num in enumerate(active_phases):
        pi = get_or_create_phase(project, phase_num)
        val = phase_values[phase_num]
        prog = phase_progress.get(phase_num, 0)
        d_start, d_end = dates[idx] if idx < len(dates) else (None, None)

        # Update phase dates if empty
        if not pi.planned_start_date and d_start:
            pi.planned_start_date = d_start
            pi.planned_end_date = d_end
        if prog > 0 and not pi.actual_start_date and d_start:
            pi.actual_start_date = d_start + timedelta(days=2)
        if prog >= 100 and not pi.actual_end_date and d_end:
            pi.actual_end_date = d_end + timedelta(days=1)
        pi.progress_pct = Decimal(str(prog))
        pi.total_value = Decimal(str(val))
        pi.save()

        # Create service for this phase
        if phase_num <= 4:
            svc_tmpl = PHASE_SVC[phase_num]
            pro = lead_pro
        elif phase_num == 6:
            svc_tmpl = PHASE_SVC[6]  # Renders
            pro = viz_pro
        else:
            continue  # phase 5 has no template

        actual_start = (d_start + timedelta(days=2)) if prog > 0 and d_start else None
        actual_end_svc = (d_end + timedelta(days=1)) if prog >= 100 and d_end else None

        create_service(
            project, pi, svc_tmpl, val, prog,
            professional=pro,
            proj_start=d_start,
            proj_end=d_end,
        )

        # Add Recorrido Virtual in phase 6 if requested
        if phase_num == 6 and include_recorrido:
            rec_val = int(val * 0.6)
            # Adjust renders value
            pi.total_value = Decimal(str(val + rec_val))
            pi.save()
            create_service(
                project, pi, SVC_RECORRIDO, rec_val, prog,
                professional=viz_pro,
                proj_start=d_start,
                proj_end=d_end,
            )


def fill_milestones(project, completed_through=None):
    """
    Create standard milestones for a project.
    completed_through: date up to which milestones are completed.
    """
    start = project.planned_start_date
    end = project.planned_end_date
    if not start or not end:
        return

    total = (end - start).days

    milestones_def = [
        ("KICKOFF", "Kickoff %s" % project.name[:40], start + timedelta(days=3)),
        ("PHASE_DELIVERY", "Entrega Investigación", start + timedelta(days=int(total * 0.15))),
        ("CLIENT_REVIEW", "Revisión Concepto con cliente", start + timedelta(days=int(total * 0.35))),
        ("PHASE_DELIVERY", "Entrega Diseño", start + timedelta(days=int(total * 0.6))),
        ("FINAL_DELIVERY", "Entrega Final", end - timedelta(days=5)),
    ]

    for i, (ms_type, name, planned) in enumerate(milestones_def):
        code = "HITO-%d" % (i + 1)
        actual = None
        if completed_through and planned <= completed_through:
            actual = planned + timedelta(days=1)
        create_milestone(project, ms_type, name, code, planned, actual)


# ===================================================================
# MAIN: Process each project
# ===================================================================

print("\n" + "=" * 80)
print("FILLING MISSING PROJECT DATA")
print("=" * 80)

for project in Project.objects.all().order_by("id"):
    pid = project.id
    status = project.status
    progress = float(project.current_progress_pct)
    total_val = float(project.total_value)
    existing_svcs = ServiceInstance.objects.filter(project=project).count()
    existing_ms = project.milestones.count()
    existing_phases = project.phase_instances.count()

    print("\n--- Project %d (%s) - %s ---" % (pid, status, project.name))
    print("    Value=%s | Progress=%s%% | Phases=%d | Services=%d | Milestones=%d" % (
        total_val, progress, existing_phases, existing_svcs, existing_ms))

    # Skip projects that are already well-populated
    if existing_svcs >= 4 and existing_ms >= 3:
        print("    SKIP: Already well-populated")
        continue

    # === DETERMINE WHAT TO FILL ===

    if status == "CANCELLED":
        # Project 19: minimal data - was started but cancelled early
        # Only phase 1 and 2, partial services
        if existing_svcs == 0:
            vals = {1: int(total_val * 0.10), 2: int(total_val * 0.15)}
            progs = {1: 100, 2: 30}
            fill_full_project(project, vals, progs)
        if existing_ms == 0:
            fill_milestones(project, completed_through=None)
        continue

    if status == "PLANNING":
        # Planning: phases defined but no progress, milestones planned
        if existing_phases == 0:
            # Create all 6 phases with zero progress
            for pn in range(1, 7):
                get_or_create_phase(project, pn)
        if existing_ms == 0:
            fill_milestones(project, completed_through=None)
        continue

    # --- ACTIVE / PAUSED / COMPLETED projects ---

    # Determine project type based on name/value
    name_lower = project.name.lower()
    is_render_project = ("render" in name_lower or "recorrido" in name_lower
                         or "maqueta" in name_lower)
    is_big_project = total_val >= 50000000
    include_recorrido = (is_render_project or is_big_project or total_val >= 30000000)

    # Calculate value distribution based on project type
    if is_render_project and total_val < 40000000:
        # Visualization-focused project: most value in phase 6
        phase_values = {
            1: int(total_val * 0.05),
            2: int(total_val * 0.10),
            6: int(total_val * 0.85),
        }
    elif total_val >= 100000000:
        # Large project: full phases
        phase_values = {
            1: int(total_val * 0.05),
            2: int(total_val * 0.10),
            3: int(total_val * 0.20),
            4: int(total_val * 0.30),
            6: int(total_val * 0.35),
        }
    else:
        # Standard project: all design phases
        phase_values = {
            1: int(total_val * 0.08),
            2: int(total_val * 0.15),
            3: int(total_val * 0.22),
            4: int(total_val * 0.30),
            6: int(total_val * 0.25),
        }

    # Calculate progress per phase based on overall project progress
    phase_progress = {}
    if status == "COMPLETED":
        for pn in phase_values:
            phase_progress[pn] = 100
    elif status == "PAUSED":
        # Paused: some phases done, current one partial
        sorted_phases = sorted(phase_values.keys())
        accumulated = 0
        for pn in sorted_phases:
            weight = phase_values[pn] / total_val * 100 if total_val else 0
            if accumulated + weight <= progress:
                phase_progress[pn] = 100
                accumulated += weight
            elif accumulated < progress:
                remaining = progress - accumulated
                phase_progress[pn] = min(100, remaining / weight * 100) if weight else 0
                accumulated = progress
            else:
                phase_progress[pn] = 0
    else:
        # Active: distribute progress across phases
        sorted_phases = sorted(phase_values.keys())
        accumulated = 0
        for pn in sorted_phases:
            weight = phase_values[pn] / total_val * 100 if total_val else 0
            if accumulated + weight <= progress:
                phase_progress[pn] = 100
                accumulated += weight
            elif accumulated < progress:
                remaining = progress - accumulated
                phase_progress[pn] = round(min(100, remaining / weight * 100), 2) if weight else 0
                accumulated = progress
            else:
                phase_progress[pn] = 0

    # Only fill services if project is missing them
    if existing_svcs < len(phase_values):
        fill_full_project(project, phase_values, phase_progress,
                          include_recorrido=include_recorrido)

    # Fill milestones
    if existing_ms == 0:
        if status == "COMPLETED":
            # All milestones completed
            fill_milestones(project, completed_through=project.planned_end_date or date.today())
        elif progress > 0 and project.planned_start_date:
            # Some milestones may be completed
            days_into = int((project.planned_end_date - project.planned_start_date).days * progress / 100) if project.planned_end_date else 0
            cutoff = project.planned_start_date + timedelta(days=days_into)
            fill_milestones(project, completed_through=cutoff)
        else:
            fill_milestones(project, completed_through=None)

# --- Assign professionals to services that don't have them ---
print("\n--- Assigning professionals to unassigned services ---")
for project in Project.objects.all().order_by("id"):
    lead_pro, viz_pro = PRO_ASSIGNMENTS.get(project.id, (PRO_CAROLINA, PRO_JUANPABLO))
    for svc in ServiceInstance.objects.filter(project=project, assigned_professional__isnull=True):
        if svc.phase_instance and svc.phase_instance.order == 6:
            svc.assigned_professional = viz_pro
        else:
            svc.assigned_professional = lead_pro
        svc.save()
        print("  Project %d: assigned %s to %s" % (
            project.id, svc.assigned_professional, svc.name[:40]))

# --- Ensure all phases have consistent progress ---
print("\n--- Syncing phase progress from services ---")
for pi in ProjectPhaseInstance.objects.all():
    svcs = pi.service_instances.all()
    if svcs.exists():
        total_val = sum(float(s.total_value) for s in svcs)
        if total_val > 0:
            weighted_prog = sum(float(s.progress_pct) * float(s.total_value) for s in svcs) / total_val
        else:
            weighted_prog = sum(float(s.progress_pct) for s in svcs) / svcs.count()
        pi.progress_pct = Decimal(str(round(weighted_prog, 2)))
        pi.save()


# --- Final summary ---
print("\n" + "=" * 80)
print("FINAL SUMMARY")
print("=" * 80)
for p in Project.objects.all().order_by("id"):
    phases = p.phase_instances.count()
    svcs = ServiceInstance.objects.filter(project=p).count()
    ms = p.milestones.count()
    print("ID=%2d | %-12s | phases=%d | services=%2d | milestones=%d | %s" % (
        p.id, p.status, phases, svcs, ms, p.name[:50]))

print("\nDone!")
