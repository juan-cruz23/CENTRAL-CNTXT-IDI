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
        self._seed_dsign_services()
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
            {"code": "00", "name": "Proyecto", "description": "Servicios transversales de gestión de proyecto."},
            {"code": "01", "name": "Urbanismo", "description": "Acciones de diseño urbano y parcelación."},
            {"code": "02", "name": "Edificación", "description": "Acciones de diseño de edificaciones."},
            {"code": "03", "name": "Complementario", "description": "Acciones complementarias: paisajismo, especificaciones, RPH."},
            {"code": "04", "name": "Espacio Interior", "description": "Acciones de diseño de espacios interiores."},
            {"code": "05", "name": "Todos", "description": "Aplica a todas las sub categorías."},
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
    def _seed_dsign_services(self):
        from apps.services.models import ProjectCategory, ProjectPhase, ServiceSubCategory, ServiceTemplate
        from apps.organizations.models import OperativeLine
        from apps.accounts.models import Role

        dsign = OperativeLine.objects.get(code="DSIGN")

        def ph(n):
            if n is None:
                return None
            return ProjectPhase.objects.get(number=n)

        def cat(code):
            return ProjectCategory.objects.get(code=code)

        _subcat_cache = {s.code: s for s in ServiceSubCategory.objects.all()}
        _role_cache = {r.code: r for r in Role.objects.all()}

        def subcat(code):
            return _subcat_cache.get(code)

        def role(code):
            return _role_cache.get(code)

        # Campos: code, name, cat, phase, subcat, hours, price (COP), margin_pct, description
        # hours y price provienen de D.sign DATA (suma por servicio). 0 = sin data.
        # subcat = código de ServiceSubCategory (00=Proyecto, 01=Urb, 02=Edif, 03=Comp, 04=Int)
        services = [
            # ── D0. Proyecto ─────────────────────────────────────────────────
            {
                "code": "D0.1", "cat": "D0", "phase": 1, "subcat": "00", "role": "LA", "hours": 7.6, "price": 696788, "margin": 30,
                "name": "Diagnóstico del proyecto y preliminares",
                "desc": "Etapa crucial que implica la recopilación y análisis de información relevante para el proyecto arquitectónico. Incluye visita al lugar, estudio de normativa, análisis del entorno y diagnóstico del estado actual.",
            },
            {
                "code": "D0.2", "cat": "D0", "phase": 1, "subcat": "00", "role": "LA", "hours": 31.2, "price": 2851396, "margin": 30,
                "name": "Análisis de determinantes y conceptualización",
                "desc": "Interpretación de determinantes físicas, ambientales, normativas y de programa para generar el concepto rector del proyecto arquitectónico.",
            },
            {
                "code": "D0.3", "cat": "D0", "phase": 1, "subcat": "00", "role": "LA", "hours": 20.7, "price": 1973852, "margin": 30,
                "name": "Presentación de desarrollo arquitectónico",
                "desc": "Exposición visual y oral que muestra el avance del desarrollo arquitectónico al cliente, integrando planimetría, renders y memoria descriptiva.",
            },
            {
                "code": "D0.4", "cat": "D0", "phase": None, "subcat": "00", "role": "LA", "hours": 0, "price": 0, "margin": 20,
                "name": "Presupuesto para ejecución de obra",
                "desc": "Documento que estima el costo total de la obra, desglosando materiales, mano de obra y costos indirectos por capítulos.",
            },
            {
                "code": "D0.5", "cat": "D0", "phase": None, "subcat": "00", "role": "LA", "hours": 0, "price": 0, "margin": 20,
                "name": "Construcción de Ficha Maestra",
                "desc": "La ficha maestra centraliza toda la información del proyecto en un solo lugar, consolidando datos técnicos, normativos, comerciales y de seguimiento.",
            },
            # ── D1. Parcelaciones y Condominios — Fase 1 ─────────────────────
            {
                "code": "D1.1", "cat": "D1", "phase": 1, "subcat": "01", "role": "LA", "hours": 44.6, "price": 4209362, "margin": 30,
                "name": "Modelo Tridimensional Viewer 360, Escala De Urbanismo (Fase 1)",
                "desc": "Modelo tridimensional interactivo a escala de urbanismo que permite visualizar el conjunto del proyecto en su contexto territorial durante la fase conceptual.",
            },
            {
                "code": "D1.2", "cat": "D1", "phase": 1, "subcat": "03", "role": "LA", "hours": 18.6, "price": 1552706, "margin": 20,
                "name": "Modelado Tridimensional Viewer 360, Elemento Complementario (Fase 1)",
                "desc": "Modelado de elementos complementarios del proyecto (zonas comunes, equipamientos, paisajismo) en formato interactivo Viewer 360 para la fase conceptual.",
            },
            {
                "code": "D1.3", "cat": "D1", "phase": 1, "subcat": "02", "role": "LA", "hours": 39.3, "price": 3709146, "margin": 30,
                "name": "Modelo Tridimensional, Viewer 360 150, Edificación (Fase 1)",
                "desc": "Modelo tridimensional con Viewer 360 de las edificaciones del proyecto (casas, edificios, unidades) para visualización conceptual en Fase 1.",
            },
            {
                "code": "D1.4", "cat": "D1", "phase": 1, "subcat": "01", "role": "LA", "hours": 36.9, "price": 3482633, "margin": 30,
                "name": "Planimetría Arquitectónica del Urbanismo (Fase 1)",
                "desc": "Planos arquitectónicos del urbanismo del proyecto: implantación, vías, manzanas, lotes y áreas comunes para la fase conceptual.",
            },
            {
                "code": "D1.5", "cat": "D1", "phase": 1, "subcat": "03", "role": "LA", "hours": 14.6, "price": 1174394, "margin": 20,
                "name": "Planimetría Arquitectónica, Elemento complementario (Fase 1)",
                "desc": "Elaboración de planimetría arquitectónica de los elementos complementarios del proyecto en fase conceptual.",
            },
            {
                "code": "D1.6", "cat": "D1", "phase": 1, "subcat": "02", "role": "LA", "hours": 32.4, "price": 2611110, "margin": 20,
                "name": "Planimetría Arquitectónica, Edificación (Fase 1)",
                "desc": "Producción de planimetría arquitectónica de las edificaciones del proyecto para la fase conceptual.",
            },
            # ── D1. Parcelaciones y Condominios — Fase 2 ─────────────────────
            {
                "code": "D1.7", "cat": "D1", "phase": 2, "subcat": "01", "role": "LA", "hours": 54.2, "price": 3974418, "margin": 15,
                "name": "Modelo Tridimensional, Viewer 360, Escala de Urbanismo (Fase 2)",
                "desc": "Modelo tridimensional actualizado a mayor nivel de detalle en escala de urbanismo para la fase técnica del proyecto.",
            },
            {
                "code": "D1.8", "cat": "D1", "phase": 2, "subcat": "03", "role": "LA", "hours": 31.0, "price": 2585252, "margin": 20,
                "name": "Modelo Tridimensional, Viewer 360, Elemento Complementario (Fase 2)",
                "desc": "Modelo tridimensional detallado de elementos complementarios con mayor precisión técnica para la fase de desarrollo.",
            },
            {
                "code": "D1.9", "cat": "D1", "phase": 2, "subcat": "02", "role": "LA", "hours": 50.1, "price": 3894021, "margin": 20,
                "name": "Modelo Tridimensional, Viewer 360, Edificación (Fase 2)",
                "desc": "Modelo tridimensional de edificaciones con alto nivel de detalle para la fase de desarrollo técnico.",
            },
            {
                "code": "D1.10", "cat": "D1", "phase": 2, "subcat": "01", "role": "LA", "hours": 47.2, "price": 3669797, "margin": 20,
                "name": "Planimetría Arquitectónica del Urbanismo (Fase 2)",
                "desc": "Paquete de planos orientado hacia la especificidad y planificación técnica del urbanismo: redes, secciones, detalles de vías y espacios públicos.",
            },
            {
                "code": "D1.11", "cat": "D1", "phase": 2, "subcat": "03", "role": "SUPP", "hours": 7.3, "price": 558695, "margin": 30,
                "name": "Planimetría Arquitectónica, Elemento Complementario (Fase 2)",
                "desc": "Planimetría arquitectónica detallada de los elementos complementarios del proyecto en fase de desarrollo técnico.",
            },
            {
                "code": "D1.12", "cat": "D1", "phase": 2, "subcat": "02", "role": "LA", "hours": 17.9, "price": 1578850, "margin": 30,
                "name": "Planimetría Arquitectónica, Edificación (Fase 2)",
                "desc": "Planimetría arquitectónica detallada de las edificaciones del proyecto en fase de desarrollo técnico.",
            },
            {
                "code": "D1.13", "cat": "D1", "phase": 2, "subcat": "01", "role": "LA", "hours": 44.2, "price": 3699708, "margin": 20,
                "name": "Especificaciones del Urbanismo (Fase 2)",
                "desc": "Formatos detallados de especificaciones técnicas del urbanismo: materiales, acabados, normas constructivas y criterios de ejecución.",
            },
            {
                "code": "D1.14", "cat": "D1", "phase": 2, "subcat": "03", "role": "LA", "hours": 33.4, "price": 2710124, "margin": 30,
                "name": "Especificaciones de Elemento Complementario (Fase 2)",
                "desc": "Formatos detallados de especificaciones técnicas de los elementos complementarios del proyecto.",
            },
            {
                "code": "D1.15", "cat": "D1", "phase": 2, "subcat": "02", "role": "LA", "hours": 31.4, "price": 2302523, "margin": 15,
                "name": "Especificaciones de Edificaciones (Fase 2)",
                "desc": "Formatos detallados de especificaciones técnicas de las edificaciones del proyecto.",
            },
            # ── D1. Parcelaciones y Condominios — Fase 3 ─────────────────────
            {
                "code": "D1.16", "cat": "D1", "phase": 3, "subcat": "01", "role": "LA", "hours": 67.8, "price": 6196302, "margin": 30,
                "name": "Modelo a detalle constructivo de urbanismo",
                "desc": "Modelo tridimensional a nivel de detalle constructivo del urbanismo, apto para coordinación de obra y replanteo.",
            },
            {
                "code": "D1.17", "cat": "D1", "phase": 3, "subcat": "02", "role": "LA", "hours": 88.8, "price": 7090758, "margin": 20,
                "name": "Modelo a detalle constructivo de edificación",
                "desc": "Representación tridimensional precisa que abarca dimensiones, composición espacial y materialidad de las edificaciones para ejecución de obra.",
            },
            {
                "code": "D1.18", "cat": "D1", "phase": 3, "subcat": "01", "role": "LA", "hours": 170.9, "price": 15618703, "margin": 30,
                "name": "Planimetría Arquitectónica de Detalle para ejecución de obra de Urbanismo",
                "desc": "Planos detallados para ejecución de obra del urbanismo: detalles constructivos, secciones, especificaciones gráficas y notas técnicas.",
            },
            {
                "code": "D1.19", "cat": "D1", "phase": 3, "subcat": "02", "role": "LA", "hours": 67.9, "price": 5480507, "margin": 20,
                "name": "Planimetría Arquitectónica de Detalle para ejecución de obra de Edificación",
                "desc": "Paquete de planos de detalle para ejecución de obra de las edificaciones: plantas, cortes, fachadas y detalles constructivos.",
            },
            {
                "code": "D1.20", "cat": "D1", "phase": 3, "subcat": "01", "role": "LA", "hours": 45.5, "price": 3944542, "margin": 20,
                "name": "Especificaciones del Urbanismo del proyecto",
                "desc": "Formato detallado de especificaciones técnicas y constructivas del urbanismo para la fase de ejecución.",
            },
            {
                "code": "D1.21", "cat": "D1", "phase": 3, "subcat": "02", "role": "LA", "hours": 39.1, "price": 3155932, "margin": 20,
                "name": "Especificaciones de Edificación",
                "desc": "Conjunto de documentos que detallan de manera específica a nivel cualitativo y cuantitativo los materiales y sistemas constructivos de las edificaciones.",
            },
            {
                "code": "D1.22", "cat": "D1", "phase": 3, "subcat": "01", "role": "LA", "hours": 16.2, "price": 1264691, "margin": 15,
                "name": "Plano de Punteo para RPH",
                "desc": "Documento gráfico que muestra la distribución y delimitación de las distintas unidades privadas y comunes para el Reglamento de Propiedad Horizontal.",
            },
            {
                "code": "D1.23", "cat": "D1", "phase": 3, "subcat": "02", "role": "DM", "hours": 30.5, "price": 3177887, "margin": 40,
                "name": "Manual Anexo para RPH",
                "desc": "Manual anexo al Reglamento de Propiedad Horizontal con normas de uso, mantenimiento, acabados permitidos y especificaciones de las unidades.",
            },
            {
                "code": "D1.24", "cat": "D1", "phase": None, "subcat": "01", "role": "LA", "hours": 42.8, "price": 3897821, "margin": 30,
                "name": "Subdivisión Predial y Cabida de un proyecto",
                "desc": "Análisis preliminar y conceptual de subdivisión predial y cabida del proyecto para gestión ante autoridades de planeación.",
            },
            {
                "code": "D1.25", "cat": "D1", "phase": 3, "subcat": "03", "role": "LA", "hours": 14.9, "price": 1410986, "margin": 30,
                "name": "Modelo a detalle constructivo de elemento complementario (Fase 3)",
                "desc": "",
            },
            {
                "code": "D1.26", "cat": "D1", "phase": 3, "subcat": "03", "role": "SUPP", "hours": 6.2, "price": 552329, "margin": 30,
                "name": "Planimetría Arquitectónica, Elemento Complementario (Fase 3)",
                "desc": "",
            },
            # ── D2. Edificación en Altura ─────────────────────────────────────
            {
                "code": "D2.1", "cat": "D2", "phase": 1, "subcat": "02", "role": "LA", "hours": 254.3, "price": 24761122, "margin": 30,
                "name": "Modelo Tridimensional, Viewer 360 150, Edificación en Altura (Fase 1)",
                "desc": "",
            },
            {
                "code": "D2.2", "cat": "D2", "phase": 1, "subcat": "02", "role": "LA", "hours": 132.8, "price": 12533705, "margin": 30,
                "name": "Planimetría Arquitectónica de Edificación en Altura (Fase 1)",
                "desc": "",
            },
            {
                "code": "D2.3", "cat": "D2", "phase": 2, "subcat": "02", "role": "LA", "hours": 42.7, "price": 3091925, "margin": 10,
                "name": "Modelo Tridimensional, Viewer 360, Edificación en Altura (Fase 2)",
                "desc": "",
            },
            {
                "code": "D2.4", "cat": "D2", "phase": 2, "subcat": "02", "role": "LA", "hours": 17.9, "price": 1363043, "margin": 15,
                "name": "Planimetría Arquitectónica de Edificación en Altura (Fase 2)",
                "desc": "",
            },
            {
                "code": "D2.5", "cat": "D2", "phase": 2, "subcat": "02", "role": "LA", "hours": 29.4, "price": 2373003, "margin": 20,
                "name": "Especificaciones de Edificación en Altura (Fase 2)",
                "desc": "",
            },
            {
                "code": "D2.6", "cat": "D2", "phase": 3, "subcat": "02", "role": "LA", "hours": 74.8, "price": 5994844, "margin": 16,
                "name": "Modelo Tridimensional, Viewer 360, Edificación en Altura (Fase 3)",
                "desc": "",
            },
            {
                "code": "D2.7", "cat": "D2", "phase": 3, "subcat": "02", "role": "LA", "hours": 80.3, "price": 6128349, "margin": 15,
                "name": "Planimetría Arquitectónica de Edificación en Altura (Fase 3)",
                "desc": "",
            },
            {
                "code": "D2.8", "cat": "D2", "phase": 3, "subcat": "02", "role": "LA", "hours": 34.7, "price": 2648241, "margin": 15,
                "name": "Especificaciones de Edificación en Altura Volumen 2 (Fase 3)",
                "desc": "",
            },
            # ── D3. Vivienda Campestre ────────────────────────────────────────
            {
                "code": "D3.1", "cat": "D3", "phase": None, "subcat": "02", "role": "LA", "hours": 38.3, "price": 3500271, "margin": 30,
                "name": "Diagnóstico del proyecto y preliminares",
                "desc": "Servicio enfocado en la creación de un modelo tridimensional interactivo del entorno y estudio de determinantes para vivienda campestre.",
            },
            {
                "code": "D3.2", "cat": "D3", "phase": 1, "subcat": "02", "role": "LA", "hours": 34.0, "price": 3010582, "margin": 30,
                "name": "Planimetría Arquitectónica de Vivienda Campestre (Fase 1)",
                "desc": "Desarrollo de los planos arquitectónicos básicos para la fase conceptual de vivienda campestre: plantas, cortes y fachadas.",
            },
            {
                "code": "D3.3", "cat": "D3", "phase": 2, "subcat": "02", "role": "LA", "hours": 23.7, "price": 2124838, "margin": 30,
                "name": "Especificaciones de Vivienda Campestre (Fase 2)",
                "desc": "Propuesta preliminar de materiales para la construcción de la vivienda campestre con criterios técnicos y estéticos.",
            },
            {
                "code": "D3.4", "cat": "D3", "phase": 2, "subcat": "02", "role": "LA", "hours": 34.7, "price": 3171264, "margin": 30,
                "name": "Modelo Tridimensional, Viewer 360 150, Vivienda Campestre (Fase 2)",
                "desc": "Modelo tridimensional detallado de la vivienda campestre con Viewer 360 para la fase de desarrollo técnico.",
            },
            {
                "code": "D3.5", "cat": "D3", "phase": 2, "subcat": "02", "role": "LA", "hours": 17.9, "price": 1632241, "margin": 30,
                "name": "Planimetría Arquitectónica de Vivienda Campestre (Fase 2)",
                "desc": "Planimetría arquitectónica detallada de la vivienda campestre para la fase de desarrollo técnico.",
            },
            {
                "code": "D3.6", "cat": "D3", "phase": None, "subcat": "02", "role": "LA", "hours": 16.0, "price": 2572963, "margin": 15,
                "name": "Replanteo de la vivienda en campo",
                "desc": "Replanteo físico de la vivienda campestre en el terreno para verificación de cotas, linderos y alineaciones antes del inicio de obra.",
            },
            {
                "code": "D3.7", "cat": "D3", "phase": 3, "subcat": "02", "role": "LA", "hours": 56.8, "price": 4165073, "margin": 15,
                "name": "Modelo Tridimensional, Viewer 360 150, Vivienda Campestre (Fase 3)",
                "desc": "Representación digital 3D de vivienda campestre en Fase 3 diseñada para comunicar detalles constructivos y materialidad final.",
            },
            {
                "code": "D3.8", "cat": "D3", "phase": 3, "subcat": "02", "role": "LA", "hours": 49.4, "price": 4367032, "margin": 30,
                "name": "Planimetría Arquitectónica de Vivienda Campestre (Fase 3)",
                "desc": "Planimetría arquitectónica detallada de la vivienda campestre con detalles constructivos para la fase de ejecución de obra.",
            },
            {
                "code": "D3.9", "cat": "D3", "phase": 3, "subcat": "02", "role": "LA", "hours": 30.1, "price": 2660884, "margin": 30,
                "name": "Especificaciones de Vivienda Campestre (Fase 3)",
                "desc": "Especificaciones técnicas y constructivas detalladas de la vivienda campestre para la fase de ejecución.",
            },
            {
                "code": "D3.10", "cat": "D3", "phase": 1, "subcat": "02", "role": "SUPP", "hours": 12.9, "price": 906680, "margin": 10,
                "name": "Personal Shopper de lote lite (Fase 1)",
                "desc": "",
            },
            {
                "code": "D3.11", "cat": "D3", "phase": 1, "subcat": "02", "role": "SUPP", "hours": 7.9, "price": 545247, "margin": 15,
                "name": "Personal Shopper de lote Advanced (Fase 1)",
                "desc": "",
            },
            # ── D4. Comercial ─────────────────────────────────────────────────
            {
                "code": "D4.1", "cat": "D4", "phase": None, "subcat": "03", "role": "LA", "hours": 56.4, "price": 5318566, "margin": 30,
                "name": "Propuesta Conceptual y de Layout Funcional Tridimensional",
                "desc": "",
            },
            {
                "code": "D4.2", "cat": "D4", "phase": None, "subcat": "03", "role": "LA", "hours": 62.6, "price": 5908207, "margin": 30,
                "name": "Modelo y Planimetría Arquitectónica Técnica para Montaje de Stand",
                "desc": "",
            },
            {
                "code": "D4.3", "cat": "D4", "phase": None, "subcat": "03", "role": "LA", "hours": 53.8, "price": 4181603, "margin": 20,
                "name": "Presupuesto, cantidades Para Producción de Stand",
                "desc": "",
            },
            # ── D6. Diseño Interior ───────────────────────────────────────────
            {
                "code": "D6.1", "cat": "D6", "phase": None, "subcat": "04", "role": "LA", "hours": 44.6, "price": 4000179, "margin": 30,
                "name": "Conceptualización de propuesta y cabida 3D preliminar",
                "desc": "Materialización de una idea inicial de transformación espacial a través de un modelo 3D preliminar que define distribución, alturas y estilo.",
            },
            {
                "code": "D6.2", "cat": "D6", "phase": None, "subcat": "00", "role": "LA", "hours": 20.8, "price": 1963110, "margin": 30,
                "name": "Look & Feel",
                "desc": "Construcción de coherencia visual y temática del proyecto de diseño interior: paleta de colores, materiales, texturas y referencias de estilo.",
            },
            {
                "code": "D6.3", "cat": "D6", "phase": None, "subcat": "04", "role": "LA", "hours": 30.0, "price": 2831409, "margin": 30,
                "name": "Modelo tridimensional fase 2 del Espacio Interior",
                "desc": "Modelo tridimensional detallado del espacio interior con materialidad y mobiliario para la fase de desarrollo técnico.",
            },
            {
                "code": "D6.4", "cat": "D6", "phase": None, "subcat": "04", "role": "LA", "hours": 92.5, "price": 6782910, "margin": 15,
                "name": "Planimetría Arquitectónica de Diseño Interior",
                "desc": "Planos técnicos detallados que definen distribución, dimensiones, acabados y especificaciones del diseño interior.",
            },
            {
                "code": "D6.5", "cat": "D6", "phase": None, "subcat": "04", "role": "LA", "hours": 28.0, "price": 2315878, "margin": 20,
                "name": "Especificaciones, experiencia de compra y cantidades de obra",
                "desc": "Desglose de especificaciones técnicas, listado de materiales con cantidades y guía de experiencia de compra para el proyecto de diseño interior.",
            },
            {
                "code": "D6.6", "cat": "D6", "phase": 1, "subcat": "04", "role": "LA", "hours": 61.0, "price": 4398529, "margin": 18,
                "name": "Diseña Tu Interior (Fase 1)",
                "desc": "",
            },
            {
                "code": "D6.7", "cat": "D6", "phase": 1, "subcat": "04", "role": "LA", "hours": 69.0, "price": 4975385, "margin": 18,
                "name": "Renueva tu Interior (Fase 1)",
                "desc": "",
            },
            # ── D7. Select ────────────────────────────────────────────────────
            {
                "code": "D7.1", "cat": "D7", "phase": 1, "subcat": "02", "role": "LA", "hours": 55.8, "price": 4503862, "margin": 20,
                "name": "Select — Servicio 1",
                "desc": "",
            },
            {
                "code": "D7.2", "cat": "D7", "phase": 1, "subcat": "02", "role": "LA", "hours": 24.1, "price": 1945217, "margin": 20,
                "name": "Select — Servicio 2",
                "desc": "",
            },
        ]

        for s in services:
            obj, created = ServiceTemplate.objects.update_or_create(
                code=s["code"],
                defaults={
                    "name": s["name"],
                    "category": cat(s["cat"]),
                    "phase": ph(s["phase"]),
                    "subcategory": subcat(s.get("subcat", "00")),
                    "responsible_role": role(s.get("role")),
                    "operative_line": dsign,
                    "base_unit_price": s["price"],
                    "estimated_hours": s["hours"],
                    "target_margin_pct": s["margin"],
                    "description": s["desc"],
                    "is_active": True,
                },
            )
            self.stdout.write(f"  {'+ ' if created else '~ '}ServiceTemplate: {obj.code} — {obj.name[:60]}")

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
