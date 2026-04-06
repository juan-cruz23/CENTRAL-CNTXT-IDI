"""
Management command: seed_cntxt_masters
Carga los datos maestros reales de CNTXT desde el análisis del archivo
05. Services_05.25.xlsm.

Idempotente: usa get_or_create / update_or_create. Se puede ejecutar
múltiples veces sin duplicar registros.

Uso:
    python3 manage.py seed_cntxt_masters
"""

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Carga maestros reales de CNTXT: BusinessUnit, OperativeLine, Role, ProjectCategory"

    def handle(self, *args, **options):
        self._seed_business_units()
        self._seed_operative_lines()
        self._seed_roles()
        self._seed_project_categories()
        self._seed_service_subcategories()
        self._seed_project_phases()
        self._seed_hardware()
        self._seed_software()
        self._seed_operational_expense_types()
        self.stdout.write(self.style.SUCCESS("✓ Maestros CNTXT cargados correctamente."))

    # ------------------------------------------------------------------
    def _seed_business_units(self):
        from apps.organizations.models import BusinessUnit

        units = [
            {
                "code": "MADE",
                "name": "MADE",
                "description": "Unidad de negocio de diseño arquitectónico y visualización.",
            },
            {
                "code": "SELECT",
                "name": "SELECT",
                "description": "Unidad de negocio residencial — proyecto piloto Select.",
            },
        ]
        for u in units:
            obj, created = BusinessUnit.objects.update_or_create(
                code=u["code"],
                defaults={"name": u["name"], "description": u["description"], "is_active": True},
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}BusinessUnit: {obj.code} — {obj.name}")

    # ------------------------------------------------------------------
    def _seed_operative_lines(self):
        from apps.organizations.models import BusinessUnit, OperativeLine

        made = BusinessUnit.objects.get(code="MADE")
        select = BusinessUnit.objects.get(code="SELECT")

        lines = [
            {
                "code": "DSIGN",
                "name": "D.sign",
                "description": "Diseño arquitectónico: modelación, planimetría, especificaciones.",
                "business_unit": made,
            },
            {
                "code": "VSUAL",
                "name": "V.sual",
                "description": "Visualización: renders, videos, recorridos 360°, plataformas web.",
                "business_unit": made,
            },
            {
                "code": "TVTAS",
                "name": "Tech Ventas",
                "description": "Tecnología y herramientas de apoyo comercial.",
                "business_unit": select,
            },
            {
                "code": "IFIN",
                "name": "Intel Financiera",
                "description": "Inteligencia financiera y reportes de rentabilidad.",
                "business_unit": made,
            },
        ]
        for ln in lines:
            obj, created = OperativeLine.objects.update_or_create(
                code=ln["code"],
                defaults={
                    "name": ln["name"],
                    "description": ln["description"],
                    "business_unit": ln["business_unit"],
                    "is_active": True,
                },
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}OperativeLine: {obj.code} — {obj.name}")

    # ------------------------------------------------------------------
    def _seed_roles(self):
        from apps.accounts.models import Role

        # Tarifas/hora en COP según hoja Listas del archivo Services_05.25.xlsm
        roles = [
            # ── V.sual ──────────────────────────────────────────────
            {
                "code": "VM",
                "name": "Visual Manager",
                "description": "Líder de la línea V.sual. Gestión, dirección creativa y control de calidad.",
                "default_hourly_rate": 22796,
                "is_leader": True,
                "can_access_financials": True,
            },
            {
                "code": "VL",
                "name": "Visual Leader",
                "description": "Responsable técnico de proyectos V.sual. Renders, animaciones y web.",
                "default_hourly_rate": 17730,
                "is_leader": False,
                "can_access_financials": False,
            },
            {
                "code": "VS",
                "name": "Visual Support",
                "description": "Soporte operativo V.sual. Modelación 3D, edición y postproducción.",
                "default_hourly_rate": 15198,
                "is_leader": False,
                "can_access_financials": False,
            },
            {
                "code": "PC",
                "name": "PC (Freelance Visual)",
                "description": "Colaborador externo de apoyo en línea V.sual.",
                "default_hourly_rate": 10000,
                "is_leader": False,
                "can_access_financials": False,
            },
            # ── D.sign ──────────────────────────────────────────────
            {
                "code": "DM",
                "name": "Design Manager",
                "description": "Líder de la línea D.sign. Gestión, dirección de diseño y control de calidad.",
                "default_hourly_rate": 22796,
                "is_leader": True,
                "can_access_financials": True,
            },
            {
                "code": "LA",
                "name": "Leader Architect",
                "description": "Arquitecto líder de proyecto. Responsable técnico del diseño.",
                "default_hourly_rate": 20263,
                "is_leader": False,
                "can_access_financials": False,
            },
            {
                "code": "SUPP",
                "name": "Support Architect",
                "description": "Arquitecto de soporte. Planimetría, especificaciones y detalles.",
                "default_hourly_rate": 17730,
                "is_leader": False,
                "can_access_financials": False,
            },
            {
                "code": "JUN",
                "name": "Junior Architect",
                "description": "Arquitecto junior. Apoyo en desarrollo y documentación.",
                "default_hourly_rate": 11651,
                "is_leader": False,
                "can_access_financials": False,
            },
            {
                "code": "INT",
                "name": "Intern Architect",
                "description": "Practicante de arquitectura. Tareas de apoyo y aprendizaje.",
                "default_hourly_rate": 10132,
                "is_leader": False,
                "can_access_financials": False,
            },
        ]
        for r in roles:
            obj, created = Role.objects.update_or_create(
                code=r["code"],
                defaults={
                    "name": r["name"],
                    "description": r["description"],
                    "default_hourly_rate": r["default_hourly_rate"],
                    "is_leader": r["is_leader"],
                    "can_access_financials": r["can_access_financials"],
                    "is_active": True,
                },
            )
            self.stdout.write(
                f"  {'+ ' if created else '~ '}Role: {obj.code} — {obj.name} (${obj.default_hourly_rate:,}/h)"
            )

    # ------------------------------------------------------------------
    def _seed_service_subcategories(self):
        from apps.services.models import ServiceSubCategory

        subcategories = [
            {"code": "00", "name": "N/A", "description": "Sin sub categoría aplicable."},
            {"code": "01", "name": "Urbanismo", "description": "Acciones de diseño urbano y parcelación."},
            {"code": "02", "name": "Edificación", "description": "Acciones de diseño de edificaciones exteriores."},
            {"code": "03", "name": "Complementario", "description": "Acciones complementarias: interiores, paisajismo, especificaciones."},
            {"code": "04", "name": "Todos", "description": "Aplica a todas las sub categorías."},
        ]
        for s in subcategories:
            obj, created = ServiceSubCategory.objects.update_or_create(
                code=s["code"],
                defaults={"name": s["name"], "description": s["description"], "is_active": True},
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}ServiceSubCategory: {obj.code} — {obj.name}")

    # ------------------------------------------------------------------
    def _seed_operational_expense_types(self):
        from apps.financials.models import OperationalExpenseType

        expenses = [
            "Gastos Administrativos",
            "Gastos Financieros",
            "Gastos de Ventas",
        ]
        for name in expenses:
            obj, created = OperationalExpenseType.objects.update_or_create(
                name=name,
                defaults={"is_active": True},
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}ExpenseType: {obj.name}")

    # ------------------------------------------------------------------
    def _seed_hardware(self):
        from apps.services.models import Hardware

        # Valores de la hoja Listas — nombre en blanco para completar después
        hardware = [
            {"name": "", "value": 10_000_000, "depreciation_per_hour": 4222},
            {"name": "", "value": 8_500_000,  "depreciation_per_hour": 3588},
            {"name": "", "value": 8_000_000,  "depreciation_per_hour": 3377},
        ]
        for h in hardware:
            obj, created = Hardware.objects.get_or_create(
                value=h["value"],
                defaults={"name": h["name"], "depreciation_per_hour": h["depreciation_per_hour"], "is_active": True},
            )
            label = obj.name or f"(sin nombre) ${obj.value:,.0f}"
            self.stdout.write(f"  {'+ ' if created else '~ '}Hardware: {label} — ${obj.depreciation_per_hour:,.0f}/h")

    # ------------------------------------------------------------------
    def _seed_software(self):
        from apps.services.models import Software

        software = [
            {"name": "SketchUp (SKP)",    "annual_value": 1_400_000,  "hourly_value": 3411},
            {"name": "Lumion",             "annual_value": 6_600_000,  "hourly_value": 3411},
            {"name": "V-Ray",              "annual_value": 3_300_000,  "hourly_value": 3411},
            {"name": "Revit",              "annual_value": 12_400_000, "hourly_value": 3411},
            {"name": "Adobe Photoshop",    "annual_value": 451_000,    "hourly_value": 3411},
        ]
        for s in software:
            obj, created = Software.objects.update_or_create(
                name=s["name"],
                defaults={"annual_value": s["annual_value"], "hourly_value": s["hourly_value"], "is_active": True},
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}Software: {obj.name} — ${obj.annual_value:,.0f}/año")

    # ------------------------------------------------------------------
    def _seed_project_phases(self):
        from apps.services.models import ProjectPhase

        phases = [
            {"number": 1, "name": "Fase 1", "description": "Conceptual / Preliminar. Diagnóstico, conceptualización y propuesta inicial."},
            {"number": 2, "name": "Fase 2", "description": "Desarrollo / Técnico. Planimetría técnica, especificaciones y coordinación."},
            {"number": 3, "name": "Fase 3", "description": "Detalle Constructivo / Ejecución. Detalles constructivos y seguimiento en obra."},
        ]
        for p in phases:
            obj, created = ProjectPhase.objects.update_or_create(
                number=p["number"],
                defaults={"name": p["name"], "description": p["description"]},
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}ProjectPhase: {obj.number} — {obj.name}")

    # ------------------------------------------------------------------
    def _seed_project_categories(self):
        from apps.services.models import ProjectCategory

        # Categorías de proyecto según estructura D.sign del archivo Services
        # Estas categorías determinan qué tipo de proyecto es y qué plantilla
        # de prerequisitos / servicios aplica.
        categories = [
            {
                "code": "D0",
                "name": "Proyecto",
                "description": "Servicios transversales de gestión: diagnóstico, conceptualización, presentaciones, presupuesto y ficha maestra.",
            },
            {
                "code": "D1",
                "name": "Parcelaciones y Condominios",
                "description": "Proyectos de urbanismo, edificación y complementarios en parcelaciones y condominios. Incluye Fase 1, Fase 2 y Fase 3.",
            },
            {
                "code": "D2",
                "name": "Edificación en Altura",
                "description": "Edificios multifamiliares y usos mixtos. Modelos, planimetría y especificaciones por fase.",
            },
            {
                "code": "D3",
                "name": "Vivienda Campestre",
                "description": "Proyectos de vivienda campestre y personal shopper de lote.",
            },
            {
                "code": "D4",
                "name": "Comercial",
                "description": "Proyectos comerciales: stands, layouts y espacios de venta.",
            },
            {
                "code": "D5",
                "name": "Industrial",
                "description": "Proyectos de arquitectura industrial. Categoría declarada, servicios en desarrollo.",
            },
            {
                "code": "D6",
                "name": "Diseño Interior",
                "description": "Proyectos de diseño de interiores: look & feel, Diseña Tu Interior, Renueva Tu Interior.",
            },
            {
                "code": "D7",
                "name": "Select",
                "description": "Categoría especial para el proyecto piloto Select — unidad de vivienda residencial.",
            },
            {
                "code": "D8",
                "name": "Hotelería",
                "description": "Proyectos hoteleros. Categoría declarada, servicios en desarrollo.",
            },
            {
                "code": "D10",
                "name": "Equipamientos",
                "description": "Equipamientos urbanos y dotacionales. Categoría declarada, servicios en desarrollo.",
            },
        ]
        for c in categories:
            obj, created = ProjectCategory.objects.update_or_create(
                code=c["code"],
                defaults={
                    "name": c["name"],
                    "description": c["description"],
                    "is_active": True,
                },
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}ProjectCategory: {obj.code} — {obj.name}")
