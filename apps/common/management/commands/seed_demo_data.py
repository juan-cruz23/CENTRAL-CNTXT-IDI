"""
Seed realistic demo data for Central Contexto 2.0.
Creates: categories, phases, service templates, clients, team members,
projects with services, payment milestones, and EVM snapshots.
Requires seed_data to have been run first (roles, systems, BUs, holidays).
"""
from datetime import date, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seed demo projects and related data for Central Contexto 2.0"

    def handle(self, *args, **options):
        self.stdout.write("Seeding demo data...")
        self._seed_categories_and_phases()
        self._seed_service_templates()
        self._seed_clients()
        self._seed_team()
        self._seed_projects()
        self._seed_evm_snapshots()
        self._seed_capacity()
        self._seed_milestones()
        self._seed_profitability()
        self._seed_documents()
        self._seed_rfis()
        self._seed_satisfaction()
        self._seed_alerts()
        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully!"))

    def _seed_categories_and_phases(self):
        from apps.services.models import ProjectCategory, ProjectPhase

        categories = [
            {"code": "ARQ", "name": "Arquitectura", "description": "Proyectos de diseño arquitectónico"},
            {"code": "INT", "name": "Interiorismo", "description": "Proyectos de diseño de interiores"},
            {"code": "VIS", "name": "Visualización", "description": "Renders y recorridos virtuales"},
            {"code": "BRD", "name": "Branding Espacial", "description": "Identidad y branding para espacios"},
            {"code": "URB", "name": "Urbanismo", "description": "Diseño urbano y paisajismo"},
        ]
        for cat in categories:
            ProjectCategory.objects.update_or_create(code=cat["code"], defaults=cat)

        phases = [
            {"number": 1, "name": "Investigación y Análisis", "description": "Levantamiento de información y análisis del sitio"},
            {"number": 2, "name": "Conceptualización", "description": "Desarrollo del concepto de diseño"},
            {"number": 3, "name": "Diseño Esquemático", "description": "Plantas, cortes y fachadas esquemáticas"},
            {"number": 4, "name": "Desarrollo de Diseño", "description": "Detalle técnico y especificaciones"},
            {"number": 5, "name": "Documentación Técnica", "description": "Planos constructivos y memorias"},
            {"number": 6, "name": "Visualización Final", "description": "Renders, recorridos y presentación final"},
        ]
        for phase in phases:
            ProjectPhase.objects.update_or_create(number=phase["number"], defaults=phase)

        self.stdout.write(f"  {len(categories)} categorías, {len(phases)} fases")

    def _seed_service_templates(self):
        from apps.services.models import ProjectCategory, ProjectPhase, ServiceTemplate, ServiceActivity
        from apps.accounts.models import Role

        cat_arq = ProjectCategory.objects.get(code="ARQ")
        cat_int = ProjectCategory.objects.get(code="INT")
        cat_vis = ProjectCategory.objects.get(code="VIS")
        p1 = ProjectPhase.objects.get(number=1)
        p2 = ProjectPhase.objects.get(number=2)
        p3 = ProjectPhase.objects.get(number=3)
        p4 = ProjectPhase.objects.get(number=4)
        p6 = ProjectPhase.objects.get(number=6)
        role_la = Role.objects.get(code="LA")
        role_int = Role.objects.get(code="INT")
        role_vs = Role.objects.get(code="VS")
        role_vl = Role.objects.get(code="VL")
        role_dm = Role.objects.get(code="DM")

        templates = [
            {
                "code": "ARQ-INV-01", "name": "Levantamiento Arquitectónico",
                "category": cat_arq, "phase": p1, "base_unit_price": 3500000,
                "estimated_hours": 40, "estimated_days": 10,
                "activities": [
                    ("Visita de campo y registro fotográfico", role_la, 8),
                    ("Medición y levantamiento dimensional", role_la, 16),
                    ("Digitalización de planos existentes", role_vl, 16),
                ],
            },
            {
                "code": "ARQ-CON-01", "name": "Concepto Arquitectónico",
                "category": cat_arq, "phase": p2, "base_unit_price": 8000000,
                "estimated_hours": 80, "estimated_days": 20,
                "activities": [
                    ("Análisis de referentes", role_la, 12),
                    ("Moodboard y paleta de materiales", role_int, 8),
                    ("Esquema conceptual en planta", role_la, 24),
                    ("Volumetría 3D exploratoria", role_vl, 20),
                    ("Presentación al cliente", role_la, 16),
                ],
            },
            {
                "code": "INT-ESQ-01", "name": "Diseño Esquemático Interior",
                "category": cat_int, "phase": p3, "base_unit_price": 12000000,
                "estimated_hours": 120, "estimated_days": 30,
                "activities": [
                    ("Layout de mobiliario y distribución", role_int, 24),
                    ("Selección de acabados y materiales", role_int, 16),
                    ("Diseño de iluminación", role_int, 12),
                    ("Planos esquemáticos (plantas y cortes)", role_la, 32),
                    ("Coordinación con ingenierías", role_la, 16),
                    ("Renders esquemáticos", role_vs, 20),
                ],
            },
            {
                "code": "ARQ-DES-01", "name": "Desarrollo de Diseño Arquitectónico",
                "category": cat_arq, "phase": p4, "base_unit_price": 15000000,
                "estimated_hours": 160, "estimated_days": 40,
                "activities": [
                    ("Detalle de fachadas", role_la, 32),
                    ("Especificaciones técnicas", role_la, 24),
                    ("Planos de detalle constructivo", role_la, 40),
                    ("Coordinación BIM", role_vl, 32),
                    ("Revisión y ajustes", role_la, 32),
                ],
            },
            {
                "code": "VIS-REN-01", "name": "Paquete de Renders",
                "category": cat_vis, "phase": p6, "base_unit_price": 6000000,
                "estimated_hours": 60, "estimated_days": 15,
                "activities": [
                    ("Modelado 3D detallado", role_vs, 20),
                    ("Texturizado e iluminación", role_vs, 16),
                    ("Renderizado (6 vistas)", role_vs, 12),
                    ("Post-producción", role_dm, 12),
                ],
            },
            {
                "code": "VIS-REC-01", "name": "Recorrido Virtual 360",
                "category": cat_vis, "phase": p6, "base_unit_price": 9000000,
                "estimated_hours": 80, "estimated_days": 20,
                "activities": [
                    ("Modelado 3D completo", role_vs, 30),
                    ("Texturizado de alta calidad", role_vs, 16),
                    ("Setup de recorrido interactivo", role_vl, 18),
                    ("Post-producción y entrega", role_dm, 16),
                ],
            },
        ]

        count = 0
        for t in templates:
            activities = t.pop("activities")
            st, created = ServiceTemplate.objects.update_or_create(
                code=t["code"],
                defaults={**t, "target_margin_pct": 25},
            )
            if created:
                count += 1
            for i, (act_name, act_role, act_hours) in enumerate(activities, 1):
                ServiceActivity.objects.update_or_create(
                    service_template=st, order=i,
                    defaults={"name": act_name, "responsible_role": act_role, "estimated_hours": act_hours},
                )

        self.stdout.write(f"  {len(templates)} plantillas de servicio ({count} nuevas)")

    def _seed_clients(self):
        from apps.projects.models import Client

        clients = [
            {"name": "Constructora Bolívar", "company": "Grupo Bolívar S.A.", "category": "BLACK", "email": "proyectos@bolivar.com.co", "phone": "601-3456789"},
            {"name": "Amarilo S.A.S.", "company": "Amarilo S.A.S.", "category": "GOLD", "email": "comercial@amarilo.com.co", "phone": "601-7654321"},
            {"name": "Arquitectura & Concreto", "company": "A&C S.A.S.", "category": "GOLD", "email": "info@ayc.com.co", "phone": "604-2345678"},
            {"name": "Inversiones Metrópoli", "company": "Grupo Metrópoli", "category": "SILVER", "email": "gestion@metropoli.co", "phone": "601-8901234"},
            {"name": "Hotel Estelar", "company": "Hoteles Estelar S.A.", "category": "BLACK", "email": "diseño@estelar.com", "phone": "601-5678901"},
        ]
        for c in clients:
            Client.objects.update_or_create(name=c["name"], defaults=c)

        self.stdout.write(f"  {len(clients)} clientes")

    def _seed_team(self):
        from apps.accounts.models import Role, UserRole

        team = [
            {"username": "carolina.mesa", "first_name": "Carolina", "last_name": "Mesa", "email": "carolina@cntxt.com.co", "role_code": "LA", "hourly_rate": 90000},
            {"username": "santiago.restrepo", "first_name": "Santiago", "last_name": "Restrepo", "email": "santiago@cntxt.com.co", "role_code": "LA", "hourly_rate": 85000},
            {"username": "valentina.garcia", "first_name": "Valentina", "last_name": "García", "email": "valentina@cntxt.com.co", "role_code": "INT", "hourly_rate": 75000},
            {"username": "juan.lopez", "first_name": "Juan Pablo", "last_name": "López", "email": "juan@cntxt.com.co", "role_code": "VS", "hourly_rate": 70000},
            {"username": "camila.ortiz", "first_name": "Camila", "last_name": "Ortiz", "email": "camila@cntxt.com.co", "role_code": "VL", "hourly_rate": 60000},
            {"username": "andres.valencia", "first_name": "Andrés", "last_name": "Valencia", "email": "andres@cntxt.com.co", "role_code": "DM", "hourly_rate": 55000},
        ]
        for m in team:
            role_code = m.pop("role_code")
            rate = m.pop("hourly_rate")
            user, created = User.objects.update_or_create(
                username=m["username"],
                defaults={**m, "hourly_rate": rate},
            )
            if created:
                user.set_password("cntxt2026")
                user.save()
            role = Role.objects.get(code=role_code)
            UserRole.objects.update_or_create(user=user, role=role, defaults={"is_primary": True})

        self.stdout.write(f"  {len(team)} miembros de equipo")

    def _seed_projects(self):
        from apps.projects.models import Client, Project, ProjectPhaseInstance, ServiceInstance, ProjectPrerequisite
        from apps.services.models import ProjectCategory, ProjectPhase, ServiceTemplate
        from apps.financials.models import PaymentMilestone
        from apps.organizations.models import BusinessUnit, OperativeLine

        cat_arq = ProjectCategory.objects.get(code="ARQ")
        cat_int = ProjectCategory.objects.get(code="INT")
        cat_vis = ProjectCategory.objects.get(code="VIS")
        made = BusinessUnit.objects.get(code="MADE")
        select = BusinessUnit.objects.get(code="SELECT")
        ol_dv = OperativeLine.objects.get(code="DV")
        ol_vis = OperativeLine.objects.get(code="VIS")
        ol_tv = OperativeLine.objects.get(code="TV")

        carolina = User.objects.get(username="carolina.mesa")
        santiago = User.objects.get(username="santiago.restrepo")
        valentina = User.objects.get(username="valentina.garcia")
        juan = User.objects.get(username="juan.lopez")
        camila = User.objects.get(username="camila.ortiz")
        andres = User.objects.get(username="andres.valencia")

        client_bolivar = Client.objects.get(name="Constructora Bolívar")
        client_amarilo = Client.objects.get(name="Amarilo S.A.S.")
        client_ayc = Client.objects.get(name="Arquitectura & Concreto")
        client_metro = Client.objects.get(name="Inversiones Metrópoli")
        client_estelar = Client.objects.get(name="Hotel Estelar")

        today = date.today()

        # ── PROJECT 1: Active, 65% done, on schedule ──────────────
        p1, _ = Project.objects.update_or_create(code="CNTXT-2026-001", defaults={
            "name": "Torre Residencial Parque Central",
            "client": client_bolivar, "category": cat_arq, "client_category": "BLACK",
            "access_type": "PREMIUM", "location": "Bogotá, Chicó Norte",
            "status": "ACTIVE", "business_unit": made, "operative_line": ol_dv,
            "leader": carolina, "iva_rate": 19,
            "planned_start_date": today - timedelta(days=90),
            "planned_end_date": today + timedelta(days=60),
            "actual_start_date": today - timedelta(days=88),
            "total_value": Decimal("53500000"),
            "current_progress_pct": Decimal("65.00"),
            "schedule_deviation_pct": Decimal("2.50"),
            "profitability_pct": Decimal("28.30"),
            "client_satisfaction_score": Decimal("4.50"),
        })
        self._create_phases_and_services(p1, carolina, juan, [
            ("ARQ-INV-01", 1, 100, today - timedelta(days=90), today - timedelta(days=75)),
            ("ARQ-CON-01", 2, 100, today - timedelta(days=74), today - timedelta(days=45)),
            ("INT-ESQ-01", 3, 70, today - timedelta(days=44), None),
            ("ARQ-DES-01", 4, 20, today - timedelta(days=10), None),
            ("VIS-REN-01", 6, 0, None, None),
        ])
        self._create_milestones(p1, [
            ("Anticipo 30%", Decimal("16050000"), "COLLECTED", today - timedelta(days=85)),
            ("Entrega Concepto", Decimal("10700000"), "COLLECTED", today - timedelta(days=40)),
            ("Entrega Diseño Esquemático", Decimal("10700000"), "INVOICED", None),
            ("Entrega Diseño Detallado", Decimal("10700000"), "PENDING", None),
            ("Entrega Final + Renders", Decimal("5350000"), "PENDING", None),
        ])
        self._create_prereqs(p1)

        # ── PROJECT 2: Active, 35% done, behind schedule ──────────
        p2, _ = Project.objects.update_or_create(code="CNTXT-2026-002", defaults={
            "name": "Lobby & Áreas Comunes Edificio Oasis",
            "client": client_amarilo, "category": cat_int, "client_category": "GOLD",
            "access_type": "STANDARD", "location": "Medellín, El Poblado",
            "status": "ACTIVE", "business_unit": made, "operative_line": ol_dv,
            "leader": valentina, "iva_rate": 19,
            "planned_start_date": today - timedelta(days=60),
            "planned_end_date": today + timedelta(days=50),
            "actual_start_date": today - timedelta(days=55),
            "total_value": Decimal("38000000"),
            "current_progress_pct": Decimal("35.00"),
            "schedule_deviation_pct": Decimal("-12.50"),
            "profitability_pct": Decimal("22.10"),
            "client_satisfaction_score": Decimal("3.80"),
        })
        self._create_phases_and_services(p2, valentina, camila, [
            ("ARQ-INV-01", 1, 100, today - timedelta(days=60), today - timedelta(days=48)),
            ("ARQ-CON-01", 2, 60, today - timedelta(days=47), None),
            ("INT-ESQ-01", 3, 0, None, None),
            ("VIS-REN-01", 6, 0, None, None),
        ])
        self._create_milestones(p2, [
            ("Anticipo 30%", Decimal("11400000"), "COLLECTED", today - timedelta(days=55)),
            ("Entrega Concepto", Decimal("11400000"), "PENDING", None),
            ("Entrega Esquemático + Renders", Decimal("15200000"), "PENDING", None),
        ])
        self._create_prereqs(p2)

        # ── PROJECT 3: Active, 85% done, ahead of schedule ───────
        p3, _ = Project.objects.update_or_create(code="CNTXT-2026-003", defaults={
            "name": "Recorrido Virtual Proyecto Serranía",
            "client": client_ayc, "category": cat_vis, "client_category": "GOLD",
            "access_type": "STANDARD", "location": "Bucaramanga",
            "status": "ACTIVE", "business_unit": made, "operative_line": ol_vis,
            "leader": santiago, "iva_rate": 19,
            "planned_start_date": today - timedelta(days=45),
            "planned_end_date": today + timedelta(days=15),
            "actual_start_date": today - timedelta(days=44),
            "total_value": Decimal("15000000"),
            "current_progress_pct": Decimal("85.00"),
            "schedule_deviation_pct": Decimal("10.00"),
            "profitability_pct": Decimal("32.50"),
            "client_satisfaction_score": Decimal("4.80"),
        })
        self._create_phases_and_services(p3, santiago, juan, [
            ("VIS-REN-01", 6, 100, today - timedelta(days=45), today - timedelta(days=25)),
            ("VIS-REC-01", 6, 70, today - timedelta(days=24), None),
        ])
        self._create_milestones(p3, [
            ("Anticipo 50%", Decimal("7500000"), "COLLECTED", today - timedelta(days=42)),
            ("Entrega Renders", Decimal("3750000"), "COLLECTED", today - timedelta(days=20)),
            ("Entrega Recorrido Virtual", Decimal("3750000"), "PENDING", None),
        ])

        # ── PROJECT 4: Completed ─────────────────────────────────
        p4, _ = Project.objects.update_or_create(code="CNTXT-2025-018", defaults={
            "name": "Remodelación Suite Presidencial Estelar",
            "client": client_estelar, "category": cat_int, "client_category": "BLACK",
            "access_type": "PREMIUM", "location": "Cartagena, Bocagrande",
            "status": "COMPLETED", "business_unit": made, "operative_line": ol_dv,
            "leader": carolina, "iva_rate": 19,
            "planned_start_date": today - timedelta(days=180),
            "planned_end_date": today - timedelta(days=30),
            "actual_start_date": today - timedelta(days=178),
            "actual_end_date": today - timedelta(days=25),
            "total_value": Decimal("42000000"),
            "current_progress_pct": Decimal("100.00"),
            "schedule_deviation_pct": Decimal("3.30"),
            "profitability_pct": Decimal("30.80"),
            "client_satisfaction_score": Decimal("4.90"),
        })
        self._create_phases_and_services(p4, carolina, juan, [
            ("ARQ-INV-01", 1, 100, today - timedelta(days=180), today - timedelta(days=165)),
            ("ARQ-CON-01", 2, 100, today - timedelta(days=164), today - timedelta(days=130)),
            ("INT-ESQ-01", 3, 100, today - timedelta(days=129), today - timedelta(days=80)),
            ("ARQ-DES-01", 4, 100, today - timedelta(days=79), today - timedelta(days=45)),
            ("VIS-REN-01", 6, 100, today - timedelta(days=44), today - timedelta(days=25)),
        ])
        self._create_milestones(p4, [
            ("Anticipo 30%", Decimal("12600000"), "COLLECTED", today - timedelta(days=175)),
            ("Entrega Concepto", Decimal("8400000"), "COLLECTED", today - timedelta(days=125)),
            ("Entrega Esquemático", Decimal("8400000"), "COLLECTED", today - timedelta(days=75)),
            ("Entrega Detallado", Decimal("8400000"), "COLLECTED", today - timedelta(days=40)),
            ("Entrega Final", Decimal("4200000"), "COLLECTED", today - timedelta(days=22)),
        ])
        self._create_prereqs(p4)

        # ── PROJECT 5: Planning ──────────────────────────────────
        p5, _ = Project.objects.update_or_create(code="CNTXT-2026-004", defaults={
            "name": "Sala de Ventas Torres del Parque III",
            "client": client_metro, "category": cat_int, "client_category": "SILVER",
            "access_type": "STANDARD", "location": "Bogotá, Salitre",
            "status": "PLANNING", "business_unit": select, "operative_line": ol_tv,
            "leader": santiago, "iva_rate": 19,
            "planned_start_date": today + timedelta(days=15),
            "planned_end_date": today + timedelta(days=90),
            "total_value": Decimal("28000000"),
            "current_progress_pct": Decimal("0.00"),
            "schedule_deviation_pct": Decimal("0.00"),
            "profitability_pct": Decimal("0.00"),
        })
        self._create_prereqs(p5)

        self.stdout.write("  5 proyectos con servicios, hitos y pre-requisitos")

    def _create_phases_and_services(self, project, leader, visualizer, services_data):
        from apps.projects.models import ProjectPhaseInstance, ServiceInstance
        from apps.services.models import ProjectPhase, ServiceTemplate

        for code, phase_num, progress, start, end in services_data:
            phase = ProjectPhase.objects.get(number=phase_num)
            template = ServiceTemplate.objects.get(code=code)

            pi, _ = ProjectPhaseInstance.objects.update_or_create(
                project=project, phase=phase,
                defaults={
                    "order": phase_num,
                    "planned_start_date": start,
                    "actual_start_date": start,
                    "planned_end_date": end or (start + timedelta(days=int(template.estimated_days))) if start else None,
                    "actual_end_date": end if progress == 100 else None,
                    "total_value": template.base_unit_price,
                    "progress_pct": progress,
                },
            )

            assigned = leader if "ARQ" in code or "INT" in code else visualizer
            # ServiceInstance.code is max_length=20, keep it short
            si_code = f"{project.code[-3:]}-{code[-6:]}"
            ServiceInstance.objects.update_or_create(
                project=project, phase_instance=pi, code=si_code,
                defaults={
                    "name": template.name,
                    "service_template": template,
                    "quantity": 1,
                    "unit_price": template.base_unit_price,
                    "progress_pct": progress,
                    "expected_progress_pct": min(progress + 5, 100) if progress < 100 else 100,
                    "is_checked": progress > 0,
                    "is_real_checked": progress == 100,
                    "responsible_role": template.activities.first().responsible_role if template.activities.exists() else None,
                    "assigned_professional": assigned,
                    "projected_hours": template.estimated_hours,
                    "projected_days": template.estimated_days,
                    "projected_start_date": start,
                    "actual_start_date": start,
                    "projected_end_date": end or (start + timedelta(days=int(template.estimated_days))) if start else None,
                    "actual_end_date": end if progress == 100 else None,
                },
            )

    def _create_milestones(self, project, milestones_data):
        from apps.financials.models import PaymentMilestone

        total = sum(v for _, v, _, _ in milestones_data)
        for concept, value, status, collected_date in milestones_data:
            iva = value * project.iva_rate / 100
            incidence = (value / total * 100) if total else 0
            PaymentMilestone.objects.update_or_create(
                project=project, concept=concept,
                defaults={
                    "proposed_value": value,
                    "iva_value": iva,
                    "incidence_pct": incidence,
                    "status": status,
                    "executed_value": value if status in ("COLLECTED", "INVOICED") else 0,
                    "billing_date": collected_date if status in ("COLLECTED", "INVOICED") else None,
                    "invoice_number": f"FV-{project.code[-3:]}-{concept[:3].upper()}" if status in ("COLLECTED", "INVOICED") else "",
                    "invoice_value": value + iva if status in ("COLLECTED", "INVOICED") else 0,
                    "collection_value": value + iva if status == "COLLECTED" else 0,
                    "collection_date": collected_date if status == "COLLECTED" else None,
                },
            )

    def _create_prereqs(self, project):
        from apps.projects.models import ProjectPrerequisite

        is_active = project.status in ("ACTIVE", "COMPLETED")
        prereqs = [
            ("PREREQUISITO", "Planos existentes", is_active),
            ("PREREQUISITO", "Brief del cliente", is_active),
            ("PREREQUISITO", "Contrato firmado", is_active),
            ("PREREQUISITO", "Anticipo recibido", is_active),
            ("GESTION_RIESGO", "Matriz de riesgos", project.status == "COMPLETED"),
            ("GESTION_RIESGO", "Plan de contingencia", project.status == "COMPLETED"),
            ("COMUNICACION", "Acta de inicio", is_active),
            ("COMUNICACION", "Cronograma aprobado", is_active),
        ]
        for cat, ptype, completed in prereqs:
            ProjectPrerequisite.objects.update_or_create(
                project=project, category=cat, prerequisite_type=ptype,
                defaults={
                    "name": ptype,
                    "is_completed": completed,
                    "weight_pct": Decimal("12.50"),
                },
            )

    def _seed_evm_snapshots(self):
        from apps.metrics.models import ProjectMetricSnapshot
        from apps.projects.models import Project

        today = date.today()

        # Snapshots for P1 (active, on schedule)
        p1 = Project.objects.get(code="CNTXT-2026-001")
        bac1 = p1.total_value
        for i, weeks_ago in enumerate([8, 6, 4, 2, 0]):
            snap_date = today - timedelta(weeks=weeks_ago)
            pv_pct = min(20 + i * 15, 75)
            ev_pct = min(18 + i * 14, 65)
            ac_pct = min(17 + i * 13, 60)
            pv = bac1 * pv_pct / 100
            ev = bac1 * ev_pct / 100
            ac = bac1 * ac_pct / 100
            spi = ev / pv if pv else 1
            cpi = ev / ac if ac else 1
            ProjectMetricSnapshot.objects.update_or_create(
                project=p1, snapshot_date=snap_date,
                defaults={
                    "bac": bac1, "planned_value": pv, "earned_value": ev, "actual_cost": ac,
                    "spi": round(spi, 4), "cpi": round(cpi, 4),
                    "schedule_variance": ev - pv, "cost_variance": ev - ac,
                    "eac": bac1 / cpi if cpi else bac1,
                    "etc": (bac1 - ev) / cpi if cpi else bac1 - ev,
                    "vac": bac1 - (bac1 / cpi) if cpi else 0,
                    "overall_progress_pct": ev_pct,
                    "expected_progress_pct": pv_pct,
                    "schedule_deviation_pct": ev_pct - pv_pct,
                    "total_revenue": ev, "total_costs": ac,
                    "projected_margin_pct": ((ev - ac) / ev * 100) if ev else 0,
                },
            )

        # Snapshots for P2 (active, behind schedule)
        p2 = Project.objects.get(code="CNTXT-2026-002")
        bac2 = p2.total_value
        for i, weeks_ago in enumerate([6, 4, 2, 0]):
            snap_date = today - timedelta(weeks=weeks_ago)
            pv_pct = min(15 + i * 12, 55)
            ev_pct = min(10 + i * 9, 35)
            ac_pct = min(12 + i * 11, 40)
            pv = bac2 * pv_pct / 100
            ev = bac2 * ev_pct / 100
            ac = bac2 * ac_pct / 100
            spi = ev / pv if pv else 1
            cpi = ev / ac if ac else 1
            ProjectMetricSnapshot.objects.update_or_create(
                project=p2, snapshot_date=snap_date,
                defaults={
                    "bac": bac2, "planned_value": pv, "earned_value": ev, "actual_cost": ac,
                    "spi": round(spi, 4), "cpi": round(cpi, 4),
                    "schedule_variance": ev - pv, "cost_variance": ev - ac,
                    "eac": bac2 / cpi if cpi else bac2,
                    "etc": (bac2 - ev) / cpi if cpi else bac2 - ev,
                    "vac": bac2 - (bac2 / cpi) if cpi else 0,
                    "overall_progress_pct": ev_pct,
                    "expected_progress_pct": pv_pct,
                    "schedule_deviation_pct": ev_pct - pv_pct,
                    "total_revenue": ev, "total_costs": ac,
                    "projected_margin_pct": ((ev - ac) / ev * 100) if ev else 0,
                },
            )

        # Snapshots for P3 (ahead of schedule)
        p3 = Project.objects.get(code="CNTXT-2026-003")
        bac3 = p3.total_value
        for i, weeks_ago in enumerate([4, 2, 0]):
            snap_date = today - timedelta(weeks=weeks_ago)
            pv_pct = min(30 + i * 20, 75)
            ev_pct = min(35 + i * 25, 85)
            ac_pct = min(28 + i * 18, 60)
            pv = bac3 * pv_pct / 100
            ev = bac3 * ev_pct / 100
            ac = bac3 * ac_pct / 100
            spi = ev / pv if pv else 1
            cpi = ev / ac if ac else 1
            ProjectMetricSnapshot.objects.update_or_create(
                project=p3, snapshot_date=snap_date,
                defaults={
                    "bac": bac3, "planned_value": pv, "earned_value": ev, "actual_cost": ac,
                    "spi": round(spi, 4), "cpi": round(cpi, 4),
                    "schedule_variance": ev - pv, "cost_variance": ev - ac,
                    "eac": bac3 / cpi if cpi else bac3,
                    "etc": (bac3 - ev) / cpi if cpi else bac3 - ev,
                    "vac": bac3 - (bac3 / cpi) if cpi else 0,
                    "overall_progress_pct": ev_pct,
                    "expected_progress_pct": pv_pct,
                    "schedule_deviation_pct": ev_pct - pv_pct,
                    "total_revenue": ev, "total_costs": ac,
                    "projected_margin_pct": ((ev - ac) / ev * 100) if ev else 0,
                },
            )

        # Final snapshot for P4 (completed)
        p4 = Project.objects.get(code="CNTXT-2025-018")
        bac4 = p4.total_value
        ProjectMetricSnapshot.objects.update_or_create(
            project=p4, snapshot_date=today - timedelta(days=25),
            defaults={
                "bac": bac4, "planned_value": bac4, "earned_value": bac4,
                "actual_cost": bac4 * Decimal("0.692"),
                "spi": Decimal("1.0000"), "cpi": Decimal("1.4450"),
                "schedule_variance": 0, "cost_variance": bac4 * Decimal("0.308"),
                "eac": bac4 * Decimal("0.692"), "etc": 0,
                "vac": bac4 * Decimal("0.308"),
                "overall_progress_pct": 100, "expected_progress_pct": 100,
                "schedule_deviation_pct": 0,
                "total_revenue": bac4, "total_costs": bac4 * Decimal("0.692"),
                "projected_margin_pct": Decimal("30.80"),
            },
        )

        self.stdout.write("  13 snapshots EVM")

    def _seed_capacity(self):
        from apps.capacity.models import TeamMemberCapacity, ProjectAllocation, CapacityAlert
        from apps.accounts.models import Role
        from apps.projects.models import Project

        today = date.today()
        team_users = User.objects.filter(
            username__in=[
                "carolina.mesa", "santiago.restrepo", "valentina.garcia",
                "juan.lopez", "camila.ortiz", "andres.valencia",
            ]
        )

        # TeamMemberCapacity for each team member
        for user in team_users:
            TeamMemberCapacity.objects.update_or_create(
                user=user, effective_from=today - timedelta(days=180),
                defaults={
                    "weekly_available_hours": Decimal("40.00"),
                    "effective_until": None,
                    "notes": f"Capacidad estándar de {user.get_full_name()}",
                },
            )

        # ProjectAllocation - assign people to active projects
        p1 = Project.objects.get(code="CNTXT-2026-001")
        p2 = Project.objects.get(code="CNTXT-2026-002")
        p3 = Project.objects.get(code="CNTXT-2026-003")

        carolina = User.objects.get(username="carolina.mesa")
        santiago = User.objects.get(username="santiago.restrepo")
        valentina = User.objects.get(username="valentina.garcia")
        juan = User.objects.get(username="juan.lopez")
        camila = User.objects.get(username="camila.ortiz")
        andres = User.objects.get(username="andres.valencia")

        role_la = Role.objects.get(code="LA")
        role_int = Role.objects.get(code="INT")
        role_vs = Role.objects.get(code="VS")
        role_vl = Role.objects.get(code="VL")
        role_dm = Role.objects.get(code="DM")

        allocations = [
            # Project 1 - Torre Residencial
            (carolina, p1, role_la, 20, 50),
            (juan, p1, role_vs, 12, 30),
            (camila, p1, role_vl, 8, 20),
            # Project 2 - Lobby Oasis
            (valentina, p2, role_int, 24, 60),
            (camila, p2, role_vl, 16, 40),
            (andres, p2, role_dm, 8, 20),
            # Project 3 - Recorrido Virtual
            (santiago, p3, role_la, 10, 25),
            (juan, p3, role_vs, 20, 50),
            (andres, p3, role_dm, 12, 30),
        ]
        for user, project, role, hours, pct in allocations:
            ProjectAllocation.objects.update_or_create(
                user=user, project=project,
                defaults={
                    "role": role,
                    "start_date": project.planned_start_date or today,
                    "end_date": project.planned_end_date,
                    "weekly_hours": Decimal(str(hours)),
                    "allocation_pct": Decimal(str(pct)),
                },
            )

        # CapacityAlerts
        alerts_data = [
            (camila, "OVERLOAD", today - timedelta(days=7), 48, 40,
             "Camila tiene 48h asignadas entre P1 y P2, excede su capacidad de 40h/semana"),
            (juan, "OVERLOAD", today - timedelta(days=3), 44, 40,
             "Juan tiene 44h entre P1 y P3, ligeramente sobre capacidad"),
            (andres, "UNDERLOAD", today - timedelta(days=14), 20, 40,
             "Andrés solo tiene 20h asignadas, 50% de capacidad disponible"),
        ]
        for user, atype, week, allocated, available, details in alerts_data:
            CapacityAlert.objects.update_or_create(
                user=user, alert_type=atype, week_start=week,
                defaults={
                    "allocated_hours": Decimal(str(allocated)),
                    "available_hours": Decimal(str(available)),
                    "details": details,
                    "is_resolved": False,
                },
            )

        self.stdout.write(f"  {team_users.count()} capacidades, {len(allocations)} asignaciones, {len(alerts_data)} alertas de capacidad")

    def _seed_milestones(self):
        from apps.projects.models import Milestone, Project, ProjectPhaseInstance

        today = date.today()

        projects_data = [
            ("CNTXT-2026-001", [
                ("H1-001", "Kickoff con cliente", "KICKOFF", today - timedelta(days=88), today - timedelta(days=88)),
                ("H2-001", "Entrega Investigación", "PHASE_DELIVERY", today - timedelta(days=75), today - timedelta(days=74)),
                ("H3-001", "Revisión Concepto con cliente", "CLIENT_REVIEW", today - timedelta(days=45), today - timedelta(days=44)),
                ("H4-001", "Entrega Diseño Esquemático", "PHASE_DELIVERY", today + timedelta(days=10), None),
                ("H5-001", "Entrega Final", "FINAL_DELIVERY", today + timedelta(days=55), None),
            ]),
            ("CNTXT-2026-002", [
                ("H1-002", "Kickoff Lobby Oasis", "KICKOFF", today - timedelta(days=55), today - timedelta(days=55)),
                ("H2-002", "Entrega Concepto", "PHASE_DELIVERY", today - timedelta(days=20), None),
                ("H3-002", "Revisión cliente", "CLIENT_REVIEW", today + timedelta(days=15), None),
                ("H4-002", "Entrega Final", "FINAL_DELIVERY", today + timedelta(days=45), None),
            ]),
            ("CNTXT-2026-003", [
                ("H1-003", "Kickoff Recorrido Serranía", "KICKOFF", today - timedelta(days=44), today - timedelta(days=44)),
                ("H2-003", "Entrega Renders", "PHASE_DELIVERY", today - timedelta(days=20), today - timedelta(days=20)),
                ("H3-003", "Entrega Recorrido Virtual", "FINAL_DELIVERY", today + timedelta(days=10), None),
            ]),
            ("CNTXT-2026-004", [
                ("H1-004", "Kickoff Torres del Parque III", "KICKOFF", today + timedelta(days=15), None),
                ("H2-004", "Entrega Concepto", "PHASE_DELIVERY", today + timedelta(days=45), None),
                ("H3-004", "Entrega Final", "FINAL_DELIVERY", today + timedelta(days=85), None),
            ]),
        ]

        count = 0
        for proj_code, milestones in projects_data:
            project = Project.objects.get(code=proj_code)
            pi = ProjectPhaseInstance.objects.filter(project=project).first()
            for code, name, mtype, planned, actual in milestones:
                Milestone.objects.update_or_create(
                    project=project, code=code,
                    defaults={
                        "name": name,
                        "milestone_type": mtype,
                        "phase_instance": pi,
                        "planned_date": planned,
                        "actual_date": actual,
                    },
                )
                count += 1

        self.stdout.write(f"  {count} hitos de proyecto")

    def _seed_profitability(self):
        from apps.financials.models import ProfitabilitySummary
        from apps.projects.models import Project

        summaries = [
            ("CNTXT-2026-001", "Torre Residencial - Fase Actual", 53500000, 4.5, 8200000, 9500000, 1800000, 2111111, 9500000, 34750000, 25250000, 47.20, 5611111, 31.60),
            ("CNTXT-2026-002", "Lobby Oasis - Fase Actual", 38000000, 3.0, 7000000, 8100000, 1200000, 2700000, 8100000, 13300000, 5200000, 22.10, 1733333, 15.40),
            ("CNTXT-2026-003", "Recorrido Serranía", 15000000, 1.5, 3200000, 3800000, 500000, 2533333, 3800000, 12750000, 8950000, 32.50, 5966667, 28.20),
            ("CNTXT-2025-018", "Suite Estelar - Completado", 42000000, 6.0, 12500000, 14200000, 2100000, 2366667, 14200000, 42000000, 27800000, 30.80, 4633333, 25.50),
        ]

        for code, name, value, months, analysis, costs, expenses, cpe_m, cpe_t, revenue, utility, margin, util_m, margin_m in summaries:
            project = Project.objects.get(code=code)
            ProfitabilitySummary.objects.update_or_create(
                project=project, milestone_name=name,
                defaults={
                    "value": Decimal(str(value)),
                    "months_invested": Decimal(str(months)),
                    "analysis_costs": Decimal(str(analysis)),
                    "total_costs": Decimal(str(costs)),
                    "expenses": Decimal(str(expenses)),
                    "cost_plus_expenses_monthly": Decimal(str(cpe_m)),
                    "cost_plus_expenses_total": Decimal(str(cpe_t)),
                    "revenue": Decimal(str(revenue)),
                    "utility": Decimal(str(utility)),
                    "margin_pct": Decimal(str(margin)),
                    "utility_monthly": Decimal(str(util_m)),
                    "margin_monthly_pct": Decimal(str(margin_m)),
                    "is_verified": code == "CNTXT-2025-018",
                },
            )

        self.stdout.write(f"  {len(summaries)} resúmenes de rentabilidad")

    def _seed_documents(self):
        from apps.documents.models import ProjectDocument
        from apps.projects.models import Project

        today = date.today()

        docs_data = [
            ("CNTXT-2026-001", [
                ("Contrato de Prestación de Servicios", "CONTRACT", today - timedelta(days=90), today - timedelta(days=88)),
                ("Acta de Inicio", "SUPPORT", today - timedelta(days=88), today - timedelta(days=88)),
                ("Informe de Levantamiento", "DELIVERABLE", today - timedelta(days=75), today - timedelta(days=74)),
                ("Presentación Concepto Arquitectónico", "DELIVERABLE", today - timedelta(days=45), today - timedelta(days=44)),
                ("Factura FV-001-ANT", "INVOICE", today - timedelta(days=85), today - timedelta(days=85)),
                ("Planos Esquemáticos v1", "DELIVERABLE", None, None),
            ]),
            ("CNTXT-2026-002", [
                ("Contrato Lobby Oasis", "CONTRACT", today - timedelta(days=60), today - timedelta(days=58)),
                ("Brief del Cliente", "SUPPORT", today - timedelta(days=58), today - timedelta(days=57)),
                ("Registro Fotográfico Sitio", "SUPPORT", today - timedelta(days=50), today - timedelta(days=50)),
                ("Moodboard Concepto", "DELIVERABLE", today - timedelta(days=30), None),
            ]),
            ("CNTXT-2026-003", [
                ("Contrato Recorrido Virtual", "CONTRACT", today - timedelta(days=45), today - timedelta(days=44)),
                ("Renders Entregados (6 vistas)", "DELIVERABLE", today - timedelta(days=20), today - timedelta(days=20)),
                ("Modelo 3D Fuente", "SUPPORT", today - timedelta(days=22), today - timedelta(days=22)),
            ]),
            ("CNTXT-2025-018", [
                ("Contrato Suite Presidencial", "CONTRACT", today - timedelta(days=180), today - timedelta(days=178)),
                ("Planos Constructivos Finales", "DELIVERABLE", today - timedelta(days=40), today - timedelta(days=38)),
                ("Renders Finales Suite", "DELIVERABLE", today - timedelta(days=28), today - timedelta(days=27)),
                ("Acta de Cierre", "SUPPORT", today - timedelta(days=25), today - timedelta(days=25)),
                ("Factura Final FV-018-FIN", "INVOICE", today - timedelta(days=22), today - timedelta(days=22)),
            ]),
        ]

        count = 0
        for proj_code, docs in docs_data:
            project = Project.objects.get(code=proj_code)
            for name, dtype, delivery, approval in docs:
                ProjectDocument.objects.update_or_create(
                    project=project, name=name,
                    defaults={
                        "document_type": dtype,
                        "delivery_date": delivery,
                        "approval_date": approval,
                        "access_link": "https://drive.google.com/placeholder" if dtype == "DELIVERABLE" else "",
                    },
                )
                count += 1

        self.stdout.write(f"  {count} documentos")

    def _seed_rfis(self):
        from apps.rfis.models import RFI
        from apps.projects.models import Project

        carolina = User.objects.get(username="carolina.mesa")
        valentina = User.objects.get(username="valentina.garcia")
        santiago = User.objects.get(username="santiago.restrepo")
        juan = User.objects.get(username="juan.lopez")

        p1 = Project.objects.get(code="CNTXT-2026-001")
        p2 = Project.objects.get(code="CNTXT-2026-002")
        p3 = Project.objects.get(code="CNTXT-2026-003")

        rfis_data = [
            (p1, "RFI-001-01", "Confirmación de alturas de entrepiso en torre tipo",
             carolina, "RESOLVED", "Estructural", 4, "Altura confirmada: 2.80m libre"),
            (p1, "RFI-001-02", "Especificación de acabado en fachada posterior",
             carolina, "IN_PROGRESS", "Arquitectura", 2, ""),
            (p1, "RFI-001-03", "Compatibilidad BIM con modelo estructural",
             carolina, "OPEN", "Estructural", 0, ""),
            (p2, "RFI-002-01", "Dimensiones exactas del lobby existente",
             valentina, "RESOLVED", "Arquitectura", 3, "Levantamiento láser completado, dimensiones actualizadas"),
            (p2, "RFI-002-02", "Tipo de iluminación permitida por normativa local",
             valentina, "IN_PROGRESS", "Eléctrica", 1, ""),
            (p2, "RFI-002-03", "Aprobación de paleta de materiales por administración",
             valentina, "OPEN", "Cliente", 0, ""),
            (p3, "RFI-003-01", "Archivos CAD base del proyecto Serranía",
             santiago, "RESOLVED", "Arquitectura", 2, "Archivos recibidos en formato .dwg y .rvt"),
            (p3, "RFI-003-02", "Textura de pisos especificada para renderizado",
             juan, "RESOLVED", "Interiorismo", 1, "Se usará porcelanato Portobello Beton 120x120"),
        ]

        for project, code, obs, prof, status, discipline, hours, response in rfis_data:
            RFI.objects.update_or_create(
                project=project, code=code,
                defaults={
                    "observations": obs,
                    "professional": prof,
                    "status": status,
                    "external_discipline": discipline,
                    "time_invested_hours": Decimal(str(hours)),
                    "response": response,
                },
            )

        self.stdout.write(f"  {len(rfis_data)} RFIs")

    def _seed_satisfaction(self):
        from apps.satisfaction.models import SatisfactionMeasurement, SatisfactionSurvey
        from apps.projects.models import Project, Milestone

        today = date.today()

        p1 = Project.objects.get(code="CNTXT-2026-001")
        p4 = Project.objects.get(code="CNTXT-2025-018")

        # P1 - Two measurements
        m1, _ = SatisfactionMeasurement.objects.update_or_create(
            project=p1, measurement_date=today - timedelta(days=74),
            defaults={
                "observed_emotion_pct": Decimal("85.00"),
                "spontaneous_phrase_pct": Decimal("78.00"),
                "symbolic_object_pct": Decimal("72.00"),
                "notes": "Cliente entusiasmado con el concepto, mencionó palabras como 'innovador' y 'elegante'",
            },
        )
        SatisfactionSurvey.objects.update_or_create(
            measurement=m1,
            defaults={
                "general_sensation": Decimal("88.00"),
                "clarity_and_support": Decimal("85.00"),
                "personal_effort": Decimal("80.00"),
                "team_relationship": Decimal("90.00"),
                "confidence": Decimal("87.00"),
                "perceived_value": Decimal("82.00"),
                "notes": "Cliente satisfecho con avance y comunicación del equipo",
            },
        )

        m2, _ = SatisfactionMeasurement.objects.update_or_create(
            project=p1, measurement_date=today - timedelta(days=20),
            defaults={
                "observed_emotion_pct": Decimal("90.00"),
                "spontaneous_phrase_pct": Decimal("82.00"),
                "symbolic_object_pct": Decimal("78.00"),
                "notes": "Reacción muy positiva a los avances del diseño esquemático",
            },
        )
        SatisfactionSurvey.objects.update_or_create(
            measurement=m2,
            defaults={
                "general_sensation": Decimal("92.00"),
                "clarity_and_support": Decimal("88.00"),
                "personal_effort": Decimal("85.00"),
                "team_relationship": Decimal("93.00"),
                "confidence": Decimal("90.00"),
                "perceived_value": Decimal("86.00"),
                "notes": "Mejoría notable respecto a la primera medición",
            },
        )

        # P4 - Final measurement (completed project)
        m3, _ = SatisfactionMeasurement.objects.update_or_create(
            project=p4, measurement_date=today - timedelta(days=25),
            defaults={
                "observed_emotion_pct": Decimal("95.00"),
                "spontaneous_phrase_pct": Decimal("92.00"),
                "symbolic_object_pct": Decimal("88.00"),
                "notes": "Cliente extremadamente satisfecho con el resultado final, recomendó a dos contactos",
            },
        )
        SatisfactionSurvey.objects.update_or_create(
            measurement=m3,
            defaults={
                "general_sensation": Decimal("96.00"),
                "clarity_and_support": Decimal("94.00"),
                "personal_effort": Decimal("90.00"),
                "team_relationship": Decimal("95.00"),
                "confidence": Decimal("97.00"),
                "perceived_value": Decimal("93.00"),
                "notes": "Proyecto modelo para satisfacción del cliente",
            },
        )

        self.stdout.write("  3 mediciones de satisfacción con encuestas")

    def _seed_alerts(self):
        from apps.notifications.models import Alert
        from apps.projects.models import Project

        admin = User.objects.filter(is_superuser=True).first()
        carolina = User.objects.get(username="carolina.mesa")
        valentina = User.objects.get(username="valentina.garcia")
        santiago = User.objects.get(username="santiago.restrepo")

        p1 = Project.objects.get(code="CNTXT-2026-001")
        p2 = Project.objects.get(code="CNTXT-2026-002")
        p3 = Project.objects.get(code="CNTXT-2026-003")

        alerts_data = [
            (p2, "WARNING", "SCHEDULE_DEVIATION",
             "Proyecto Lobby Oasis con retraso",
             "El proyecto CNTXT-2026-002 presenta una desviación de cronograma de -12.5%. "
             "Se recomienda revisar la asignación de recursos y priorizar entregables críticos.",
             [valentina, admin]),
            (p2, "CRITICAL", "COST_OVERRUN",
             "SPI bajo en Lobby Oasis",
             "El SPI del proyecto CNTXT-2026-002 es 0.73, por debajo del umbral de 0.90. "
             "El proyecto está generando menos valor del planeado para el costo incurrido.",
             [valentina, admin]),
            (None, "WARNING", "CAPACITY_OVERLOAD",
             "Camila Ortiz sobre-asignada",
             "Camila Ortiz tiene 48 horas asignadas esta semana contra una capacidad de 40 horas. "
             "Considere redistribuir carga entre el equipo.",
             [carolina, admin]),
            (p1, "INFO", "MILESTONE_DUE",
             "Entrega Diseño Esquemático próxima",
             "El hito 'Entrega Diseño Esquemático' del proyecto Torre Residencial "
             "está programado para dentro de 10 días.",
             [carolina, admin]),
            (p3, "INFO", "MILESTONE_DUE",
             "Entrega Recorrido Virtual próxima",
             "El hito final del proyecto Recorrido Virtual Serranía está programado "
             "para dentro de 10 días. Proyecto adelantado en cronograma.",
             [santiago, admin]),
            (p2, "WARNING", "PAYMENT_OVERDUE",
             "Factura pendiente Lobby Oasis",
             "La factura por concepto 'Entrega Concepto' del proyecto Lobby Oasis "
             "aún no ha sido facturada. El hito correspondiente ya fue alcanzado.",
             [valentina, admin]),
        ]

        for project, severity, category, title, message, targets in alerts_data:
            alert, _ = Alert.objects.update_or_create(
                title=title,
                defaults={
                    "project": project,
                    "severity": severity,
                    "category": category,
                    "message": message,
                    "is_read": False,
                    "is_resolved": False,
                },
            )
            alert.target_users.set([u for u in targets if u])

        self.stdout.write(f"  {len(alerts_data)} alertas/notificaciones")
