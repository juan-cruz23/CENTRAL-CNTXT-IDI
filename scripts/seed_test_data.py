"""
Seed de datos de prueba amplios para Central Contexto 2.0
Crea: terceros variados, proyectos con servicios, hitos de pago, snapshots EVM
Ejecutar: python3 manage.py shell < scripts/seed_test_data.py
"""
import os, sys, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

import random
from decimal import Decimal
from datetime import date, timedelta

from apps.accounts.models import User
from apps.projects.models import Project, ServiceInstance, Client, ProjectPhaseInstance
from apps.services.models import ServiceTemplate, ProjectPhase, ProjectCategory
from apps.organizations.models import BusinessUnit, OperativeLine
from apps.terceros.models import ThirdParty, ThirdPartyContact
from apps.financials.models import PaymentMilestone
from apps.metrics.models import ProjectMetricSnapshot

# ───────────────────────────────────────────────────
# Helpers
# ───────────────────────────────────────────────────
BU_MADE = BusinessUnit.objects.get(code="MADE")
BU_SELECT = BusinessUnit.objects.get(code="SELECT")

users = list(User.objects.exclude(username="admin"))
admin_user = User.objects.get(username="admin")
templates = list(ServiceTemplate.objects.all())
categories = list(ProjectCategory.objects.all())
op_lines = list(OperativeLine.objects.all())

def rand_dec(low, high, places=2):
    return Decimal(str(round(random.uniform(low, high), places)))

def rand_date(start, end):
    delta = (end - start).days
    return start + timedelta(days=random.randint(0, max(delta, 1)))

# ───────────────────────────────────────────────────
# 1. Terceros adicionales
# ───────────────────────────────────────────────────
print("Creando terceros...")

terceros_data = [
    # Clientes
    {"name": "Grupo Argos", "company": "Grupo Argos S.A.", "nit": "890900266-3",
     "relationship_type": "CLIENTE", "client_category": "BLACK",
     "email": "proyectos@grupoargos.com", "phone": "604-3198888", "city": "Medellín"},
    {"name": "Conconcreto", "company": "Conconcreto S.A.", "nit": "890900364-0",
     "relationship_type": "CLIENTE", "client_category": "BLACK",
     "email": "contratos@conconcreto.com", "phone": "604-4449999", "city": "Medellín"},
    {"name": "Pactia", "company": "Pactia S.A.S.", "nit": "900433920-1",
     "relationship_type": "CLIENTE", "client_category": "GOLD",
     "email": "desarrollo@pactia.com", "phone": "604-3222000", "city": "Medellín"},
    {"name": "Coninsa Ramón H.", "company": "Coninsa Ramón H. S.A.", "nit": "890900842-0",
     "relationship_type": "CLIENTE", "client_category": "GOLD",
     "email": "nuevos@coninsa.co", "phone": "604-4441234", "city": "Medellín"},
    {"name": "Bia Group", "company": "Bia Group S.A.S.", "nit": "901234567-8",
     "relationship_type": "CLIENTE", "client_category": "SILVER",
     "email": "info@biagroup.co", "phone": "601-7456789", "city": "Bogotá"},
    {"name": "Cubo Arquitectos", "company": "Cubo Arquitectos S.A.S.", "nit": "901345678-9",
     "relationship_type": "CLIENTE", "client_category": "SELECT",
     "email": "contacto@cuboarq.co", "phone": "604-3114567", "city": "Medellín"},
    {"name": "Londoño Gómez", "company": "Londoño Gómez Constructores", "nit": "890987654-1",
     "relationship_type": "CLIENTE", "client_category": "SILVER",
     "email": "proyectos@londonogomez.co", "phone": "604-2348900", "city": "Medellín"},
    # Prospectos
    {"name": "EPM Inmobiliaria", "company": "EPM Inmobiliaria S.A.S.", "nit": "900567890-2",
     "relationship_type": "PROSPECTO", "email": "licitaciones@epm.com.co", "city": "Medellín"},
    {"name": "Terranum", "company": "Terranum Capital S.A.S.", "nit": "900678901-3",
     "relationship_type": "PROSPECTO", "email": "negocios@terranum.co", "city": "Bogotá"},
    # Growth Partners
    {"name": "Taller de Diseño", "company": "Taller de Diseño S.A.S.", "nit": "901456789-0",
     "relationship_type": "GROWTH_PARTNER", "email": "alianza@tallerdediseno.co", "city": "Cali"},
    # Proveedores
    {"name": "Muebles y Acabados", "company": "M&A Soluciones S.A.S.", "nit": "900111222-3",
     "relationship_type": "PROVEEDOR", "email": "ventas@mya.co", "city": "Envigado"},
    {"name": "Iluminación Profesional", "company": "LightPro S.A.S.", "nit": "901222333-4",
     "relationship_type": "PROVEEDOR", "email": "cotizaciones@lightpro.co", "city": "Sabaneta"},
    # Aliados estratégicos
    {"name": "RenderCo Studios", "company": "RenderCo Studios S.A.S.", "nit": "901333444-5",
     "relationship_type": "ALIADO_ESTRATEGICO", "email": "alianzas@renderco.co", "city": "Medellín"},
    # Equipo interno
    {"name": "Equipo Freelance Vis", "company": "Contexto Freelancers",
     "relationship_type": "EQUIPO_INTERNO", "email": "freelance@contexto.co", "city": "Medellín"},
]

created_terceros = []
for td in terceros_data:
    obj, created = ThirdParty.objects.get_or_create(
        name=td["name"],
        defaults=td
    )
    created_terceros.append(obj)
    if created:
        print(f"  + {obj.name} [{obj.relationship_type}]")
    else:
        print(f"  = {obj.name} (ya existía)")

# Contactos para algunos terceros
contacts_data = [
    (created_terceros[0], "Carlos Vélez", "Director de Proyectos", "carlos.velez@grupoargos.com"),
    (created_terceros[0], "Laura Restrepo", "Coord. Compras", "laura.restrepo@grupoargos.com"),
    (created_terceros[1], "Andrés Mejía", "Gerente Técnico", "andres.mejia@conconcreto.com"),
    (created_terceros[2], "María Fernanda Gil", "VP Desarrollo", "mfgil@pactia.com"),
    (created_terceros[3], "Felipe Correa", "Dir. Comercial", "fcorrea@coninsa.co"),
    (created_terceros[4], "Natalia Sánchez", "Arquitecta Líder", "nsanchez@biagroup.co"),
]
for tp, cname, crole, cemail in contacts_data:
    ThirdPartyContact.objects.get_or_create(
        third_party=tp, name=cname,
        defaults={"role": crole, "email": cemail, "is_primary": True}
    )

# ───────────────────────────────────────────────────
# 2. Nuevos proyectos
# ───────────────────────────────────────────────────
print("\nCreando proyectos...")

clientes = ThirdParty.objects.filter(relationship_type="CLIENTE")
clientes_list = list(clientes)

projects_data = [
    # ACTIVE projects - MADE
    {
        "code": "CNTXT-2026-005", "name": "Centro Empresarial Argos Tower",
        "third_party": created_terceros[0],  # Grupo Argos
        "status": "ACTIVE", "business_unit": BU_MADE,
        "category": categories[0], "operative_line": op_lines[0],
        "client_category": "BLACK", "access_type": "PREMIUM",
        "total_value": Decimal("185000000"), "current_progress_pct": Decimal("42.50"),
        "planned_start_date": date(2025, 11, 1), "planned_end_date": date(2026, 8, 30),
        "actual_start_date": date(2025, 11, 15),
        "leader": users[0] if users else admin_user,
    },
    {
        "code": "CNTXT-2026-006", "name": "Apartamentos Vista Verde - Interiores",
        "third_party": created_terceros[1],  # Conconcreto
        "status": "ACTIVE", "business_unit": BU_MADE,
        "category": categories[2],  # Interiorismo
        "operative_line": op_lines[0],
        "client_category": "BLACK", "access_type": "PREMIUM",
        "total_value": Decimal("92000000"), "current_progress_pct": Decimal("78.00"),
        "planned_start_date": date(2025, 8, 1), "planned_end_date": date(2026, 4, 15),
        "actual_start_date": date(2025, 8, 10),
        "leader": users[1] if len(users) > 1 else admin_user,
    },
    {
        "code": "CNTXT-2026-007", "name": "Showroom Pactia Innovation Hub",
        "third_party": created_terceros[2],  # Pactia
        "status": "ACTIVE", "business_unit": BU_MADE,
        "category": categories[4],  # Branding Espacial
        "operative_line": op_lines[0],
        "client_category": "GOLD", "access_type": "PREMIUM",
        "total_value": Decimal("67000000"), "current_progress_pct": Decimal("55.00"),
        "planned_start_date": date(2025, 12, 1), "planned_end_date": date(2026, 6, 30),
        "actual_start_date": date(2025, 12, 10),
        "leader": users[2] if len(users) > 2 else admin_user,
    },
    # ACTIVE projects - SELECT
    {
        "code": "CNTXT-2026-008", "name": "Renders Urbanización El Retiro",
        "third_party": created_terceros[3],  # Coninsa
        "status": "ACTIVE", "business_unit": BU_SELECT,
        "category": categories[3],  # Visualización
        "operative_line": op_lines[1],
        "client_category": "GOLD", "access_type": "STANDARD",
        "total_value": Decimal("28000000"), "current_progress_pct": Decimal("20.00"),
        "planned_start_date": date(2026, 1, 15), "planned_end_date": date(2026, 5, 30),
        "actual_start_date": date(2026, 1, 20),
        "leader": users[3] if len(users) > 3 else admin_user,
    },
    {
        "code": "CNTXT-2026-009", "name": "Recorrido Virtual Bia Lofts",
        "third_party": created_terceros[4],  # Bia Group
        "status": "ACTIVE", "business_unit": BU_SELECT,
        "category": categories[3],  # Visualización
        "operative_line": op_lines[1],
        "client_category": "SILVER", "access_type": "STANDARD",
        "total_value": Decimal("35000000"), "current_progress_pct": Decimal("60.00"),
        "planned_start_date": date(2025, 10, 1), "planned_end_date": date(2026, 3, 31),
        "actual_start_date": date(2025, 10, 5),
        "leader": users[4] if len(users) > 4 else admin_user,
    },
    {
        "code": "CNTXT-2026-010", "name": "Maqueta Digital Cubo Residencias",
        "third_party": created_terceros[5],  # Cubo Arquitectos
        "status": "ACTIVE", "business_unit": BU_SELECT,
        "category": categories[3],  # Visualización
        "operative_line": op_lines[2],  # Tech Ventas
        "client_category": "SELECT", "access_type": "STANDARD",
        "total_value": Decimal("18500000"), "current_progress_pct": Decimal("90.00"),
        "planned_start_date": date(2025, 9, 1), "planned_end_date": date(2026, 2, 28),
        "actual_start_date": date(2025, 9, 5),
        "leader": users[0] if users else admin_user,
    },
    # PLANNING projects
    {
        "code": "CNTXT-2026-011", "name": "Diseño Interior Hotel Dann Carlton Rionegro",
        "third_party": created_terceros[6],  # Londoño Gómez
        "status": "PLANNING", "business_unit": BU_MADE,
        "category": categories[2],  # Interiorismo
        "operative_line": op_lines[0],
        "client_category": "SILVER", "access_type": "STANDARD",
        "total_value": Decimal("120000000"), "current_progress_pct": Decimal("0.00"),
        "planned_start_date": date(2026, 4, 1), "planned_end_date": date(2027, 2, 28),
        "leader": users[1] if len(users) > 1 else admin_user,
    },
    {
        "code": "CNTXT-2026-012", "name": "Urbanismo Parque Central Norte",
        "third_party": created_terceros[0],  # Grupo Argos
        "status": "PLANNING", "business_unit": BU_MADE,
        "category": categories[5],  # Urbanismo
        "operative_line": op_lines[0],
        "client_category": "BLACK", "access_type": "PREMIUM",
        "total_value": Decimal("245000000"), "current_progress_pct": Decimal("0.00"),
        "planned_start_date": date(2026, 6, 1), "planned_end_date": date(2027, 6, 30),
        "leader": users[2] if len(users) > 2 else admin_user,
    },
    # PAUSED project
    {
        "code": "CNTXT-2026-013", "name": "Remodelación Oficinas Pactia Piso 12",
        "third_party": created_terceros[2],  # Pactia
        "status": "PAUSED", "business_unit": BU_MADE,
        "category": categories[2],  # Interiorismo
        "operative_line": op_lines[0],
        "client_category": "GOLD", "access_type": "PREMIUM",
        "total_value": Decimal("58000000"), "current_progress_pct": Decimal("30.00"),
        "planned_start_date": date(2025, 7, 1), "planned_end_date": date(2026, 1, 31),
        "actual_start_date": date(2025, 7, 15),
        "leader": users[3] if len(users) > 3 else admin_user,
        "notes": "Pausado por reestructuración del cliente. Retoma estimada: abril 2026.",
    },
    # COMPLETED projects
    {
        "code": "CNTXT-2025-019", "name": "Diseño Fachada Torre Conconcreto 85",
        "third_party": created_terceros[1],  # Conconcreto
        "status": "COMPLETED", "business_unit": BU_MADE,
        "category": categories[0],  # Arquitectura
        "operative_line": op_lines[0],
        "client_category": "BLACK", "access_type": "PREMIUM",
        "total_value": Decimal("75000000"), "current_progress_pct": Decimal("100.00"),
        "planned_start_date": date(2025, 3, 1), "planned_end_date": date(2025, 10, 31),
        "actual_start_date": date(2025, 3, 5), "actual_end_date": date(2025, 11, 10),
        "leader": users[0] if users else admin_user,
    },
    {
        "code": "CNTXT-2025-020", "name": "Renders Proyecto Bia Terrazas",
        "third_party": created_terceros[4],  # Bia Group
        "status": "COMPLETED", "business_unit": BU_SELECT,
        "category": categories[3],  # Visualización
        "operative_line": op_lines[1],
        "client_category": "SILVER", "access_type": "STANDARD",
        "total_value": Decimal("22000000"), "current_progress_pct": Decimal("100.00"),
        "planned_start_date": date(2025, 5, 1), "planned_end_date": date(2025, 8, 31),
        "actual_start_date": date(2025, 5, 10), "actual_end_date": date(2025, 9, 5),
        "leader": users[4] if len(users) > 4 else admin_user,
    },
    # CANCELLED project
    {
        "code": "CNTXT-2025-021", "name": "Concepto Centro Comercial Viva Laureles",
        "third_party": created_terceros[6],  # Londoño Gómez
        "status": "CANCELLED", "business_unit": BU_MADE,
        "category": categories[0],  # Arquitectura
        "operative_line": op_lines[0],
        "client_category": "SILVER", "access_type": "STANDARD",
        "total_value": Decimal("45000000"), "current_progress_pct": Decimal("10.00"),
        "planned_start_date": date(2025, 9, 1), "planned_end_date": date(2026, 3, 31),
        "actual_start_date": date(2025, 9, 15),
        "leader": users[1] if len(users) > 1 else admin_user,
        "notes": "Cancelado: el cliente desistió del proyecto por cambio de estrategia.",
    },
]

def get_or_create_client_for_tercero(tercero):
    """Ensure a legacy Client record exists for this ThirdParty."""
    client, _ = Client.objects.get_or_create(
        name=tercero.name,
        defaults={
            "company": tercero.company or "",
            "category": tercero.client_category or "",
            "email": tercero.email or "",
            "phone": tercero.phone or "",
        }
    )
    return client

created_projects = []
for pd in projects_data:
    tp = pd.pop("third_party")
    leader = pd.pop("leader")
    category = pd.pop("category")
    ol = pd.pop("operative_line")
    bu = pd.pop("business_unit")

    # Get or create legacy Client for the ThirdParty
    client = get_or_create_client_for_tercero(tp)

    obj, created = Project.objects.get_or_create(
        code=pd["code"],
        defaults={
            **pd,
            "third_party": tp,
            "client": client,
            "leader": leader,
            "category": category,
            "operative_line": ol,
            "business_unit": bu,
        }
    )
    created_projects.append(obj)
    if created:
        print(f"  + {obj.code} | {obj.name} | {obj.status}")
    else:
        print(f"  = {obj.code} (ya existía)")


# ───────────────────────────────────────────────────
# 3. Service Instances para cada proyecto activo/completado
# ───────────────────────────────────────────────────
print("\nCreando service instances...")

def ensure_phase_instances(project):
    """Create PhaseInstances for a project if they don't exist. Returns dict of phase_pk -> PhaseInstance."""
    phases = ProjectPhase.objects.all().order_by("number")
    result = {}
    start = project.planned_start_date or date(2026, 1, 1)
    for i, phase in enumerate(phases):
        pi, _ = ProjectPhaseInstance.objects.get_or_create(
            project=project,
            phase=phase,
            defaults={
                "order": i + 1,
                "planned_start_date": start + timedelta(days=i * 30),
                "planned_end_date": start + timedelta(days=(i + 1) * 30),
                "total_value": Decimal("0"),
                "progress_pct": Decimal("0"),
            }
        )
        result[phase.pk] = pi
    return result

# Map service templates to logical phases:
# 2=Levantamiento->Phase1(Investigación), 3=Concepto->Phase2(Conceptualización),
# 4=Diseño Esquemático->Phase3, 5=Desarrollo Diseño->Phase4,
# 6=Renders->Phase6(Visualización), 7=Recorrido Virtual->Phase6
TEMPLATE_TO_PHASE = {2: 1, 3: 2, 4: 3, 5: 4, 6: 6, 7: 6, 1: 3}

def create_services_for_project(project, service_configs):
    """service_configs: list of (template_pk, hours, price, progress, expected)"""
    phase_instances = ensure_phase_instances(project)
    for i, (tpk, hours, price, prog, exp) in enumerate(service_configs, 1):
        tmpl = ServiceTemplate.objects.get(pk=tpk)
        phase_pk = TEMPLATE_TO_PHASE.get(tpk, 1)
        phase_instance = phase_instances.get(phase_pk, list(phase_instances.values())[0])
        si, created = ServiceInstance.objects.get_or_create(
            project=project,
            service_template=tmpl,
            defaults={
                "code": f"{project.code}-S{i:02d}",
                "name": tmpl.name,
                "phase_instance": phase_instance,
                "quantity": Decimal("1"),
                "unit_price": Decimal(str(price)),
                "total_value": Decimal(str(price)),
                "projected_hours": Decimal(str(hours)),
                "progress_pct": Decimal(str(prog)),
                "expected_progress_pct": Decimal(str(exp)),
                "estimated_operative_cost": Decimal(str(int(price * 0.55))),
                "incidence_pct": Decimal("0"),
                "projected_start_date": project.planned_start_date + timedelta(days=i*15),
                "projected_end_date": project.planned_start_date + timedelta(days=i*15 + 60),
            }
        )
        if created:
            print(f"    + {si.code} {si.name}")

# CNTXT-2026-005 - Centro Empresarial Argos Tower (ACTIVE 42.5%, MADE, $185M)
p005 = next(p for p in created_projects if p.code == "CNTXT-2026-005")
create_services_for_project(p005, [
    # (template_pk, hours, price, progress%, expected%)
    (2, 60, 7000000, 100, 100),     # Levantamiento
    (3, 100, 15000000, 100, 100),    # Concepto
    (5, 200, 45000000, 60, 65),     # Desarrollo Diseño
    (4, 160, 38000000, 20, 30),     # Diseño Esquemático Interior
    (6, 80, 18000000, 0, 5),        # Paquete de Renders
    (7, 120, 25000000, 0, 0),       # Recorrido Virtual
])

# CNTXT-2026-006 - Apttos Vista Verde Interiores (ACTIVE 78%, MADE, $92M)
p006 = next(p for p in created_projects if p.code == "CNTXT-2026-006")
create_services_for_project(p006, [
    (2, 40, 5000000, 100, 100),
    (3, 80, 12000000, 100, 100),
    (4, 120, 25000000, 90, 90),
    (5, 160, 30000000, 70, 75),
    (6, 60, 12000000, 40, 50),
])

# CNTXT-2026-007 - Showroom Pactia (ACTIVE 55%, MADE, $67M)
p007 = next(p for p in created_projects if p.code == "CNTXT-2026-007")
create_services_for_project(p007, [
    (3, 60, 10000000, 100, 100),
    (4, 100, 20000000, 75, 80),
    (5, 120, 22000000, 30, 35),
    (6, 40, 8000000, 0, 5),
    (7, 60, 12000000, 0, 0),
])

# CNTXT-2026-008 - Renders Urbanización El Retiro (ACTIVE 20%, SELECT, $28M)
p008 = next(p for p in created_projects if p.code == "CNTXT-2026-008")
create_services_for_project(p008, [
    (6, 80, 15000000, 30, 35),
    (7, 60, 13000000, 10, 15),
])

# CNTXT-2026-009 - Recorrido Virtual Bia Lofts (ACTIVE 60%, SELECT, $35M)
p009 = next(p for p in created_projects if p.code == "CNTXT-2026-009")
create_services_for_project(p009, [
    (7, 100, 18000000, 80, 85),
    (6, 80, 12000000, 50, 55),
    (3, 40, 5000000, 100, 100),
])

# CNTXT-2026-010 - Maqueta Digital Cubo (ACTIVE 90%, SELECT, $18.5M)
p010 = next(p for p in created_projects if p.code == "CNTXT-2026-010")
create_services_for_project(p010, [
    (7, 80, 12000000, 95, 95),
    (6, 40, 6500000, 85, 90),
])

# CNTXT-2026-013 - Remodelación Pactia Piso 12 (PAUSED 30%, MADE, $58M)
p013 = next(p for p in created_projects if p.code == "CNTXT-2026-013")
create_services_for_project(p013, [
    (2, 30, 4000000, 100, 100),
    (3, 60, 10000000, 60, 65),
    (4, 100, 20000000, 0, 10),
    (5, 120, 24000000, 0, 0),
])

# CNTXT-2025-019 - Fachada Conconcreto (COMPLETED 100%, MADE, $75M)
p019 = next(p for p in created_projects if p.code == "CNTXT-2025-019")
create_services_for_project(p019, [
    (2, 40, 5000000, 100, 100),
    (3, 80, 12000000, 100, 100),
    (5, 160, 30000000, 100, 100),
    (6, 60, 15000000, 100, 100),
    (7, 80, 13000000, 100, 100),
])

# CNTXT-2025-020 - Renders Bia Terrazas (COMPLETED 100%, SELECT, $22M)
p020 = next(p for p in created_projects if p.code == "CNTXT-2025-020")
create_services_for_project(p020, [
    (6, 60, 12000000, 100, 100),
    (7, 50, 10000000, 100, 100),
])


# ───────────────────────────────────────────────────
# 4. Payment Milestones (Hitos de Pago)
# ───────────────────────────────────────────────────
print("\nCreando hitos de pago...")

def create_milestones_for_project(project, milestones_data):
    """milestones_data: list of (concept, proposed, status, billing_date, invoice_val, collection_val, collection_date)"""
    for concept, proposed, status, billing_dt, inv_val, coll_val, coll_dt in milestones_data:
        pm, created = PaymentMilestone.objects.get_or_create(
            project=project,
            concept=concept,
            defaults={
                "proposed_value": Decimal(str(proposed)),
                "status": status,
                "billing_date": billing_dt,
                "invoice_value": Decimal(str(inv_val)) if inv_val else Decimal("0"),
                "collection_value": Decimal(str(coll_val)) if coll_val else Decimal("0"),
                "collection_date": coll_dt,
                "iva_value": Decimal(str(int(proposed * 0.19))),
                "incidence_pct": Decimal("0"),
            }
        )
        if created:
            print(f"    + {project.code}: {concept}")

# CNTXT-2026-005 - $185M
create_milestones_for_project(p005, [
    ("Anticipo 30%", 55500000, "COLLECTED", date(2025, 11, 15), 55500000, 55500000, date(2025, 12, 5)),
    ("Entrega Concepto", 37000000, "INVOICED", date(2026, 1, 30), 37000000, 0, None),
    ("Avance Diseño 50%", 37000000, "PENDING", date(2026, 4, 15), 0, 0, None),
    ("Entrega Renders", 27750000, "PENDING", date(2026, 6, 30), 0, 0, None),
    ("Entrega Final", 27750000, "PENDING", date(2026, 8, 30), 0, 0, None),
])

# CNTXT-2026-006 - $92M
create_milestones_for_project(p006, [
    ("Anticipo 30%", 27600000, "COLLECTED", date(2025, 8, 10), 27600000, 27600000, date(2025, 8, 25)),
    ("Entrega Concepto", 18400000, "COLLECTED", date(2025, 10, 15), 18400000, 18400000, date(2025, 11, 1)),
    ("Avance 60%", 18400000, "COLLECTED", date(2025, 12, 20), 18400000, 18400000, date(2026, 1, 10)),
    ("Avance 80%", 13800000, "INVOICED", date(2026, 2, 15), 13800000, 0, None),
    ("Entrega Final", 13800000, "PENDING", date(2026, 4, 15), 0, 0, None),
])

# CNTXT-2026-007 - $67M
create_milestones_for_project(p007, [
    ("Anticipo 40%", 26800000, "COLLECTED", date(2025, 12, 10), 26800000, 26800000, date(2025, 12, 28)),
    ("Avance 50%", 20100000, "INVOICED", date(2026, 3, 15), 20100000, 0, None),
    ("Entrega Final", 20100000, "PENDING", date(2026, 6, 30), 0, 0, None),
])

# CNTXT-2026-008 - $28M
create_milestones_for_project(p008, [
    ("Anticipo 50%", 14000000, "COLLECTED", date(2026, 1, 20), 14000000, 14000000, date(2026, 2, 5)),
    ("Entrega Final", 14000000, "PENDING", date(2026, 5, 30), 0, 0, None),
])

# CNTXT-2026-009 - $35M
create_milestones_for_project(p009, [
    ("Anticipo 30%", 10500000, "COLLECTED", date(2025, 10, 5), 10500000, 10500000, date(2025, 10, 20)),
    ("Avance 50%", 10500000, "COLLECTED", date(2025, 12, 15), 10500000, 10500000, date(2026, 1, 5)),
    ("Avance 80%", 7000000, "INVOICED", date(2026, 2, 28), 7000000, 0, None),
    ("Entrega Final", 7000000, "PENDING", date(2026, 3, 31), 0, 0, None),
])

# CNTXT-2026-010 - $18.5M
create_milestones_for_project(p010, [
    ("Anticipo 50%", 9250000, "COLLECTED", date(2025, 9, 5), 9250000, 9250000, date(2025, 9, 20)),
    ("Avance 75%", 4625000, "COLLECTED", date(2025, 11, 30), 4625000, 4625000, date(2025, 12, 15)),
    ("Entrega Final", 4625000, "INVOICED", date(2026, 2, 28), 4625000, 0, None),
])

# CNTXT-2025-019 - $75M (COMPLETED)
create_milestones_for_project(p019, [
    ("Anticipo 30%", 22500000, "COLLECTED", date(2025, 3, 5), 22500000, 22500000, date(2025, 3, 20)),
    ("Avance 50%", 18750000, "COLLECTED", date(2025, 5, 30), 18750000, 18750000, date(2025, 6, 15)),
    ("Avance 80%", 18750000, "COLLECTED", date(2025, 8, 31), 18750000, 18750000, date(2025, 9, 15)),
    ("Entrega Final", 15000000, "COLLECTED", date(2025, 11, 10), 15000000, 15000000, date(2025, 11, 25)),
])

# CNTXT-2025-020 - $22M (COMPLETED)
create_milestones_for_project(p020, [
    ("Anticipo 50%", 11000000, "COLLECTED", date(2025, 5, 10), 11000000, 11000000, date(2025, 5, 25)),
    ("Entrega Final", 11000000, "COLLECTED", date(2025, 9, 5), 11000000, 11000000, date(2025, 9, 20)),
])


# ───────────────────────────────────────────────────
# 5. Metric Snapshots (EVM mensual)
# ───────────────────────────────────────────────────
print("\nCreando snapshots EVM...")

def create_snapshots_for_project(project, snapshots_data):
    """snapshots_data: list of (date, bac, pv, ev, ac, pc, overall_prog, exp_prog)"""
    for snap_date, bac, pv, ev, ac, pc, overall, expected in snapshots_data:
        spi = round(ev / pv, 4) if pv > 0 else Decimal("1.0")
        cpi = round(ev / ac, 4) if ac > 0 else Decimal("1.0")
        sv = ev - pv
        cv = ev - ac
        eac = round(bac / cpi, 2) if cpi > 0 else bac
        etc = eac - ac
        vac = bac - eac

        obj, created = ProjectMetricSnapshot.objects.get_or_create(
            project=project,
            snapshot_date=snap_date,
            defaults={
                "bac": Decimal(str(bac)),
                "planned_value": Decimal(str(pv)),
                "earned_value": Decimal(str(ev)),
                "actual_cost": Decimal(str(ac)),
                "planned_cost": Decimal(str(pc)),
                "spi": Decimal(str(spi)),
                "cpi": Decimal(str(cpi)),
                "schedule_variance": Decimal(str(sv)),
                "cost_variance": Decimal(str(cv)),
                "eac": Decimal(str(eac)),
                "etc": Decimal(str(max(etc, 0))),
                "vac": Decimal(str(vac)),
                "overall_progress_pct": Decimal(str(overall)),
                "expected_progress_pct": Decimal(str(expected)),
                "schedule_deviation_pct": Decimal(str(round(overall - expected, 2))),
                "total_revenue": Decimal(str(pv)),
                "total_costs": Decimal(str(ac)),
                "projected_margin_pct": Decimal(str(round((1 - ac/bac)*100, 2) if bac > 0 else 0)),
            }
        )
        if created:
            print(f"    + {project.code}: {snap_date}")

# CNTXT-2026-005 - Argos Tower (ACTIVE 42.5%, $185M)
create_snapshots_for_project(p005, [
    #  date,             BAC,       PV,        EV,        AC,        PC,       prog, exp
    (date(2025, 12, 31), 185000000, 22000000,  20000000,  18500000,  21000000, 12.0, 15.0),
    (date(2026, 1, 31),  185000000, 48000000,  45000000,  43000000,  46000000, 25.0, 30.0),
    (date(2026, 2, 28),  185000000, 72000000,  68000000,  65000000,  70000000, 38.0, 42.0),
    (date(2026, 3, 8),   185000000, 82000000,  78500000,  76000000,  80000000, 42.5, 45.0),
])

# CNTXT-2026-006 - Vista Verde (ACTIVE 78%, $92M)
create_snapshots_for_project(p006, [
    (date(2025, 9, 30),  92000000, 12000000,  11500000,  10800000,  11000000, 13.0, 12.0),
    (date(2025, 10, 31), 92000000, 25000000,  24800000,  23500000,  24000000, 28.0, 27.0),
    (date(2025, 11, 30), 92000000, 38000000,  37000000,  36000000,  37500000, 42.0, 40.0),
    (date(2025, 12, 31), 92000000, 52000000,  51000000,  49000000,  51500000, 56.0, 55.0),
    (date(2026, 1, 31),  92000000, 65000000,  64000000,  62000000,  64500000, 68.0, 67.0),
    (date(2026, 2, 28),  92000000, 75000000,  73000000,  71000000,  74000000, 78.0, 76.0),
])

# CNTXT-2026-007 - Showroom Pactia (ACTIVE 55%, $67M)
create_snapshots_for_project(p007, [
    (date(2026, 1, 31),  67000000, 15000000,  13500000,  14000000,  14500000, 20.0, 22.0),
    (date(2026, 2, 28),  67000000, 30000000,  28000000,  29000000,  29500000, 40.0, 42.0),
    (date(2026, 3, 8),   67000000, 38000000,  36500000,  37000000,  37500000, 55.0, 55.0),
])

# CNTXT-2026-008 - Renders El Retiro (ACTIVE 20%, SELECT, $28M)
create_snapshots_for_project(p008, [
    (date(2026, 2, 28),  28000000, 6000000,   5200000,   5500000,   5800000,  18.0, 20.0),
    (date(2026, 3, 8),   28000000, 7500000,   5600000,   6000000,   7000000,  20.0, 25.0),
])

# CNTXT-2026-009 - Bia Lofts Virtual (ACTIVE 60%, SELECT, $35M)
create_snapshots_for_project(p009, [
    (date(2025, 11, 30), 35000000, 8000000,   7500000,   7000000,   7800000,  22.0, 20.0),
    (date(2025, 12, 31), 35000000, 14000000,  13500000,  13000000,  13800000, 38.0, 35.0),
    (date(2026, 1, 31),  35000000, 20000000,  19000000,  18500000,  19500000, 50.0, 48.0),
    (date(2026, 2, 28),  35000000, 24000000,  22000000,  21500000,  23500000, 60.0, 62.0),
])

# CNTXT-2026-010 - Maqueta Cubo (ACTIVE 90%, SELECT, $18.5M)
create_snapshots_for_project(p010, [
    (date(2025, 10, 31), 18500000, 5000000,   4800000,   4500000,   4900000,  25.0, 22.0),
    (date(2025, 11, 30), 18500000, 9000000,   9200000,   8500000,   8800000,  50.0, 45.0),
    (date(2025, 12, 31), 18500000, 13000000,  13500000,  12500000,  12800000, 72.0, 68.0),
    (date(2026, 1, 31),  18500000, 16000000,  16200000,  15000000,  15800000, 85.0, 82.0),
    (date(2026, 2, 28),  18500000, 17500000,  17000000,  16200000,  17200000, 90.0, 92.0),
])

# CNTXT-2025-019 - Fachada Conconcreto (COMPLETED, $75M)
create_snapshots_for_project(p019, [
    (date(2025, 4, 30),  75000000, 10000000,  9500000,   9000000,   9800000,  12.0, 13.0),
    (date(2025, 5, 31),  75000000, 20000000,  19000000,  18500000,  19500000, 25.0, 26.0),
    (date(2025, 6, 30),  75000000, 30000000,  29000000,  28000000,  29500000, 38.0, 40.0),
    (date(2025, 7, 31),  75000000, 42000000,  41000000,  39000000,  41500000, 55.0, 55.0),
    (date(2025, 8, 31),  75000000, 55000000,  54000000,  52000000,  54500000, 72.0, 73.0),
    (date(2025, 9, 30),  75000000, 65000000,  64000000,  62000000,  64500000, 85.0, 86.0),
    (date(2025, 10, 31), 75000000, 75000000,  75000000,  72000000,  74500000, 100.0, 100.0),
])

# CNTXT-2025-020 - Renders Bia Terrazas (COMPLETED, $22M)
create_snapshots_for_project(p020, [
    (date(2025, 6, 30),  22000000, 6000000,   5500000,   5200000,   5800000,  25.0, 27.0),
    (date(2025, 7, 31),  22000000, 12000000,  11500000,  11000000,  11800000, 55.0, 54.0),
    (date(2025, 8, 31),  22000000, 20000000,  19500000,  19000000,  19800000, 90.0, 90.0),
    (date(2025, 9, 5),   22000000, 22000000,  22000000,  21000000,  21800000, 100.0, 100.0),
])


# ───────────────────────────────────────────────────
# Resumen final
# ───────────────────────────────────────────────────
print("\n" + "=" * 60)
print("SEED DATA COMPLETADO")
print("=" * 60)
print(f"Terceros:     {ThirdParty.objects.count()} total")
print(f"  Clientes:   {ThirdParty.objects.filter(relationship_type='CLIENTE').count()}")
print(f"  Prospectos: {ThirdParty.objects.filter(relationship_type='PROSPECTO').count()}")
print(f"  Proveedores:{ThirdParty.objects.filter(relationship_type='PROVEEDOR').count()}")
print(f"  GP/Aliados: {ThirdParty.objects.filter(relationship_type__in=['GROWTH_PARTNER','ALIADO_ESTRATEGICO']).count()}")
print(f"Proyectos:    {Project.objects.count()} total")
print(f"  Activos:    {Project.objects.filter(status='ACTIVE').count()}")
print(f"  Planeación: {Project.objects.filter(status='PLANNING').count()}")
print(f"  Pausados:   {Project.objects.filter(status='PAUSED').count()}")
print(f"  Completados:{Project.objects.filter(status='COMPLETED').count()}")
print(f"  Cancelados: {Project.objects.filter(status='CANCELLED').count()}")
print(f"Servicios:    {ServiceInstance.objects.count()} instancias")
print(f"Hitos pago:   {PaymentMilestone.objects.count()} total")
print(f"Snapshots:    {ProjectMetricSnapshot.objects.count()} total")
print(f"\nBU MADE:   {Project.objects.filter(business_unit__code='MADE').count()} proyectos")
print(f"BU SELECT: {Project.objects.filter(business_unit__code='SELECT').count()} proyectos")
