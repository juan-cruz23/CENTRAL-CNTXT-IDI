"""
Seed data for Capacity module - TeamMemberCapacity, ProjectAllocation, CapacityAlert.
Run: DJANGO_SETTINGS_MODULE=config.settings.local ./venv/bin/python manage.py shell < scripts/seed_capacity_data.py
"""
import os
import sys
from datetime import date, timedelta
from decimal import Decimal

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from apps.accounts.models import Role, User
from apps.capacity.models import CapacityAlert, ProjectAllocation, TeamMemberCapacity
from apps.projects.models import Project

# Clear existing capacity data
print("Limpiando datos de capacidad existentes...")
CapacityAlert.objects.all().delete()
ProjectAllocation.objects.all().delete()
TeamMemberCapacity.objects.all().delete()

today = date.today()
month_start = today.replace(day=1)
three_months_ago = (month_start - timedelta(days=1)).replace(day=1) - timedelta(days=60)
three_months_ahead = month_start + timedelta(days=120)

# Get users (skip admin)
users = list(User.objects.exclude(username="admin").order_by("pk"))
active_projects = list(Project.objects.filter(status="ACTIVE").order_by("pk"))
roles = {r.code: r for r in Role.objects.all()}

print(f"Usuarios: {len(users)}, Proyectos activos: {len(active_projects)}")

# ---- TeamMemberCapacity ----
print("\nCreando capacidades del equipo...")
capacity_config = [
    # (user_idx, weekly_hours, effective_from, effective_until)
    (0, 45, three_months_ago, None),              # Carolina - lider, 45h/semana
    (1, 40, three_months_ago, None),              # Santiago - estándar
    (2, 40, three_months_ago, None),              # Valentina - estándar
    (3, 40, three_months_ago, None),              # Juan Pablo - estándar
    (4, 30, three_months_ago, None),              # Camila - medio tiempo parcial
    (5, 40, three_months_ago, None),              # Andrés - estándar
]

capacities = []
for user_idx, hours, eff_from, eff_until in capacity_config:
    if user_idx >= len(users):
        continue
    cap = TeamMemberCapacity.objects.create(
        user=users[user_idx],
        weekly_available_hours=Decimal(str(hours)),
        effective_from=eff_from,
        effective_until=eff_until,
        notes=f"Capacidad estándar {hours}h/semana",
    )
    capacities.append(cap)
    print(f"  {users[user_idx].get_full_name()}: {hours}h/semana")

# ---- ProjectAllocation ----
print("\nCreando asignaciones a proyectos...")

# Realistic allocation: each person works on 2-4 projects
# Format: (user_idx, project_idx, role_code, weekly_hours, alloc_pct, start_offset_days, duration_days)
allocation_config = [
    # Carolina Mesa - Líder, trabaja en 4 proyectos (sobrecargada: 48h de 45h)
    (0, 0, "LA", 16, 36, -60, 180),   # Torre Residencial - lider
    (0, 1, "LA", 12, 27, -30, 150),   # Lobby Edificio Oasis
    (0, 3, "LA", 10, 22, -15, 120),   # Centro Empresarial Argos
    (0, 7, "LA", 10, 22, 0, 90),      # Recorrido Virtual Bia Lofts

    # Santiago Restrepo - Visualizador Senior, 3 proyectos (bien cargado: 38h de 40h)
    (1, 0, "VS", 14, 35, -45, 160),   # Torre Residencial
    (1, 2, "VS", 12, 30, -20, 120),   # Recorrido Virtual Serranía
    (1, 5, "VS", 12, 30, -10, 100),   # Showroom Pactia

    # Valentina Garcia - Interiorista, 3 proyectos (carga normal: 32h de 40h)
    (2, 1, "INT", 14, 35, -30, 150),  # Lobby Edificio Oasis
    (2, 4, "INT", 10, 25, -15, 120),  # Apartamentos Vista Verde
    (2, 8, "INT", 8, 20, 0, 90),      # Maqueta Digital Cubo

    # Juan Pablo López - Visualizador, 3 proyectos (subcargado: 24h de 40h)
    (3, 6, "VL", 10, 25, -20, 130),   # Renders El Retiro
    (3, 7, "VL", 8, 20, -10, 100),    # Recorrido Virtual Bia Lofts
    (3, 8, "VL", 6, 15, 0, 90),       # Maqueta Digital Cubo

    # Camila Ortiz - Diseñadora Multimedia, 2 proyectos (al límite: 28h de 30h)
    (4, 2, "DM", 16, 53, -30, 120),   # Recorrido Virtual Serranía
    (4, 5, "DM", 12, 40, -15, 100),   # Showroom Pactia

    # Andrés Valencia - AI/Multimedia, 4 proyectos (sobrecargado: 44h de 40h)
    (5, 0, "AI_I", 12, 30, -45, 160), # Torre Residencial
    (5, 3, "AI_I", 10, 25, -20, 120), # Centro Empresarial Argos
    (5, 6, "AI_M", 12, 30, -10, 100), # Renders El Retiro
    (5, 8, "AI_M", 10, 25, 5, 90),    # Maqueta Digital Cubo
]

alloc_count = 0
for user_idx, proj_idx, role_code, hours, pct, start_off, duration in allocation_config:
    if user_idx >= len(users) or proj_idx >= len(active_projects):
        continue
    user = users[user_idx]
    project = active_projects[proj_idx]
    role = roles.get(role_code)
    start = today + timedelta(days=start_off)
    end = start + timedelta(days=duration)

    ProjectAllocation.objects.create(
        user=user,
        project=project,
        role=role,
        start_date=start,
        end_date=end,
        weekly_hours=Decimal(str(hours)),
        allocation_pct=Decimal(str(pct)),
        notes=f"{user.get_full_name()} en {project.code} como {role_code}",
    )
    alloc_count += 1

print(f"  {alloc_count} asignaciones creadas")

# ---- CapacityAlert ----
print("\nCreando alertas de capacidad...")

monday = today - timedelta(days=today.weekday())

alerts_config = [
    # Carolina sobrecargada esta semana
    (0, "OVERLOAD", monday, 48, 45, "Carolina tiene 48h asignadas esta semana (límite: 45h). Redistribuir carga del proyecto Bia Lofts."),
    # Carolina sobrecargada semana pasada
    (0, "OVERLOAD", monday - timedelta(weeks=1), 46, 45, "Sobrecarga semana anterior: 46h vs 45h disponibles."),
    # Andrés sobrecargado
    (5, "OVERLOAD", monday, 44, 40, "Andrés tiene 4 proyectos simultáneos. Total: 44h vs 40h disponibles."),
    # Andrés conflicto con dos proyectos
    (5, "CONFLICT", monday - timedelta(weeks=1), 44, 40, "Conflicto de horarios: entregas de Argos Tower y Renders El Retiro en la misma semana."),
    # Juan subcargado
    (3, "UNDERLOAD", monday, 24, 40, "Juan Pablo tiene solo 24h asignadas de 40h disponibles. Capacidad ociosa: 16h."),
    # Juan subcargado semana anterior
    (3, "UNDERLOAD", monday - timedelta(weeks=1), 22, 40, "Solo 22h asignadas. Considerar asignación a nuevo proyecto."),
    # Camila al límite semana pasada
    (4, "OVERLOAD", monday - timedelta(weeks=2), 32, 30, "Camila excedió su capacidad de medio tiempo: 32h vs 30h."),
    # Alerta resuelta de Santiago (semana pasada)
    (1, "OVERLOAD", monday - timedelta(weeks=3), 42, 40, "Santiago tuvo sobrecarga temporal por entrega de Recorrido Virtual."),
]

alert_count = 0
for user_idx, alert_type, week, alloc_h, avail_h, details in alerts_config:
    if user_idx >= len(users):
        continue
    alert = CapacityAlert.objects.create(
        user=users[user_idx],
        alert_type=alert_type,
        week_start=week,
        allocated_hours=Decimal(str(alloc_h)),
        available_hours=Decimal(str(avail_h)),
        details=details,
        is_resolved=(user_idx == 1),  # Solo la de Santiago está resuelta
    )
    alert_count += 1

print(f"  {alert_count} alertas creadas")

# Summary
print(f"\n--- Resumen ---")
print(f"TeamMemberCapacity: {TeamMemberCapacity.objects.count()}")
print(f"ProjectAllocation: {ProjectAllocation.objects.count()}")
print(f"CapacityAlert: {CapacityAlert.objects.count()} ({CapacityAlert.objects.filter(is_resolved=False).count()} pendientes)")
print("Done!")
