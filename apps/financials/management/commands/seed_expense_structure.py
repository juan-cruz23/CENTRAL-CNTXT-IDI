from django.core.management.base import BaseCommand

from apps.financials.models import ExpenseCategory, ExpenseSubCategory, OperationalExpenseType

CATEGORIES = [
    {"code": "I.Op",   "name": "Ingresos Operacionales",       "type": "ingreso"},
    {"code": "I.NoOp", "name": "Ingresos No Operacionales",    "type": "ingreso"},
    {"code": "C.Op",   "name": "Costos Operacionales",         "type": "costo"},
    {"code": "G.Op",   "name": "Gastos Operacionales",         "type": "gasto"},
    {"code": "G.NoOp", "name": "Gastos No Operacionales",      "type": "gasto"},
    {"code": "Imp",    "name": "Impuestos",                    "type": "impuesto"},
]

SUBCATEGORIES = [
    # ── Ingresos Operacionales ──────────────────────────────────────────────
    {"cat": "I.Op",   "code": "MADE.Urb",    "name": "MADE | Urbanístico"},
    {"cat": "I.Op",   "code": "MADE.Arq",    "name": "MADE | Arquitectónico"},
    {"cat": "I.Op",   "code": "MADE.Int",    "name": "MADE | Interiorismo"},
    {"cat": "I.Op",   "code": "SEL.Lic",     "name": "SELECT | Licencia de Uso"},
    # ── Ingresos No Operacionales ──────────────────────────────────────────
    {"cat": "I.NoOp", "code": "PER.Ces",     "name": "Permeo | Cesión"},
    # ── Costos Operacionales ───────────────────────────────────────────────
    {"cat": "C.Op",   "code": "HOp.Dir",     "name": "H. Op. | Honorarios Directivos"},
    {"cat": "C.Op",   "code": "HOp.Lid",     "name": "H. Op. | Honorarios de Liderazgo"},
    {"cat": "C.Op",   "code": "HOp.Sop",     "name": "H. Op. | Honorarios de Soporte"},
    {"cat": "C.Op",   "code": "HOp.Jun",     "name": "H. Op. | Honorarios Junior"},
    {"cat": "C.Op",   "code": "Exp.Proy",    "name": "Exp. | Experiencias de Proyectos"},
    # ── Gastos Operacionales — Administrativos ─────────────────────────────
    {"cat": "G.Op",   "code": "GAdm.Coo",   "name": "G. Adm. | Honorarios de Coordinación"},
    {"cat": "G.Op",   "code": "GAdm.Con",   "name": "G. Adm. | Honorarios Contables"},
    {"cat": "G.Op",   "code": "GAdm.Jur",   "name": "G. Adm. | Honorarios Jurídicos"},
    {"cat": "G.Op",   "code": "GAdm.FinH",  "name": "G. Adm. | Honorarios Financieros"},
    {"cat": "G.Op",   "code": "GAdm.Arr",   "name": "G. Adm. | Arrendamientos"},
    {"cat": "G.Op",   "code": "GAdm.Afi",   "name": "G. Adm. | Contribuciones y afiliaciones"},
    {"cat": "G.Op",   "code": "GAdm.Seg",   "name": "G. Adm. | Seguros"},
    {"cat": "G.Op",   "code": "GAdm.Ser",   "name": "G. Adm. | Servicios"},
    {"cat": "G.Op",   "code": "GAdm.Man",   "name": "G. Adm. | Mantenimiento y reparaciones"},
    {"cat": "G.Op",   "code": "GAdm.Div",   "name": "G. Adm. | Diversos"},
    # ── Gastos Operacionales — Ventas ──────────────────────────────────────
    {"cat": "G.Op",   "code": "GVen.Dir",   "name": "G. Ventas | Honorarios Directivos"},
    {"cat": "G.Op",   "code": "GVen.Ext",   "name": "G. Ventas | Honorarios Externos de ventas"},
    {"cat": "G.Op",   "code": "GVen.Afi",   "name": "G. Ventas | Contribuciones y afiliaciones"},
    {"cat": "G.Op",   "code": "GVen.Ser",   "name": "G. Ventas | Servicios"},
    {"cat": "G.Op",   "code": "GVen.Via",   "name": "G. Ventas | Gastos de viaje"},
    {"cat": "G.Op",   "code": "GVen.Rel",   "name": "G. Ventas | Gastos de Relacionamiento"},
    {"cat": "G.Op",   "code": "GVen.Div",   "name": "G. Ventas | Diversos"},
    # ── Gastos No Operacionales ────────────────────────────────────────────
    {"cat": "G.NoOp", "code": "GFin.Ban",   "name": "G. Fin. | Bancarios"},
    # ── Impuestos ──────────────────────────────────────────────────────────
    {"cat": "Imp",    "code": "Imp.Ren",    "name": "Renta"},
    {"cat": "Imp",    "code": "Imp.ICA",    "name": "ICA"},
    {"cat": "Imp",    "code": "Imp.4x1",    "name": "4x1000"},
]

CONCEPTS = [
    # ── I.Op — MADE ────────────────────────────────────────────────────────
    {"sub": "MADE.Urb",  "name": "Proyectos de más de 1000 m²",          "vendor": "Varios"},
    {"sub": "MADE.Arq",  "name": "Proyectos de hasta 1000 m²",           "vendor": "Varios"},
    {"sub": "MADE.Int",  "name": "Proyectos de menos de 200 m²",         "vendor": "Varios"},
    {"sub": "SEL.Lic",   "name": "Viviendas por Catálogo",               "vendor": "Varios"},
    # ── I.NoOp — Permeo ────────────────────────────────────────────────────
    {"sub": "PER.Ces",   "name": "Cesión del espacio",                   "vendor": "Permeo"},
    # ── C.Op — Honorarios Directivos ───────────────────────────────────────
    {"sub": "HOp.Dir",   "name": "Honorarios Dirección Ejecutiva",        "vendor": "Simón Cuesta Londoño"},
    {"sub": "HOp.Dir",   "name": "Honorarios Dirección Creativa",         "vendor": "Juan Pablo Castaño Ramirez"},
    {"sub": "HOp.Dir",   "name": "Honorarios Dirección Operativa",        "vendor": "Natalia A. Osorio Marín"},
    {"sub": "HOp.Dir",   "name": "Honorarios Dirección Innovación & Experiencia", "vendor": "Juan Esteban Cruz"},
    # ── C.Op — Honorarios de Liderazgo ─────────────────────────────────────
    {"sub": "HOp.Lid",   "name": "Honorarios Support de Arquitectura",    "vendor": "Daniel Felipe Lara"},
    {"sub": "HOp.Lid",   "name": "Honorarios Líder de Arquitectura",      "vendor": "Maicol J. Acosta Arango"},
    {"sub": "HOp.Lid",   "name": "Honorarios Líder Select",               "vendor": "Mateo Diaz Rendón"},
    {"sub": "HOp.Lid",   "name": "Honorarios Líder de Visualización",     "vendor": "Juan Camilo Guzmán"},
    {"sub": "HOp.Lid",   "name": "Honorarios Líder de Tecnología",        "vendor": "Nelson Carvajal"},
    # ── C.Op — Honorarios de Soporte ───────────────────────────────────────
    {"sub": "HOp.Sop",   "name": "Honorarios Support de Visualización",   "vendor": "Juan Camilo Rendón"},
    # ── C.Op — Honorarios Junior ───────────────────────────────────────────
    {"sub": "HOp.Jun",   "name": "Honorarios Arquitectura",               "vendor": "Maria José Jaramillo"},
    {"sub": "HOp.Jun",   "name": "Honorarios Arquitectura",               "vendor": "Isabela Garcés"},
    # ── C.Op — Experiencias ────────────────────────────────────────────────
    {"sub": "Exp.Proy",  "name": "Experiencias - Entrega de proyectos",   "vendor": "Varios"},
    # ── G.Op — Honorarios Coordinación ─────────────────────────────────────
    {"sub": "GAdm.Coo",  "name": "Honorarios Coordinadora Ejecutiva",     "vendor": "Jenny Rivera Escobar"},
    # ── G.Op — Honorarios Contables ────────────────────────────────────────
    {"sub": "GAdm.Con",  "name": "Contabilidad",                          "vendor": "Willian Soto"},
    # ── G.Op — Honorarios Jurídicos ────────────────────────────────────────
    {"sub": "GAdm.Jur",  "name": "Acompañamiento Jurídico",               "vendor": "ZM Consultores"},
    # ── G.Op — Honorarios Financieros ──────────────────────────────────────
    {"sub": "GAdm.FinH", "name": "Consultoría financiera",                "vendor": "Consultoría"},
    # ── G.Op — Arrendamientos ──────────────────────────────────────────────
    {"sub": "GAdm.Arr",  "name": "Arriendo Oficina CNTXT Central",        "vendor": "Alberto Alvarez SA"},
    # ── G.Op — Contribuciones y afiliaciones (Adm) ─────────────────────────
    {"sub": "GAdm.Afi",  "name": "Cloud Principal y Dominio Anual",       "vendor": "Google Workspace"},
    {"sub": "GAdm.Afi",  "name": "Hosting Mensual de CNTXT, correos y páginas operativas", "vendor": "Hostgator"},
    {"sub": "GAdm.Afi",  "name": "App para gestión Jurídica",             "vendor": "Zapsign by Truora"},
    {"sub": "GAdm.Afi",  "name": "Software de Edición y Postproducción",  "vendor": "Veo - Freepik - Software Visual"},
    {"sub": "GAdm.Afi",  "name": "Software de Ofimática",                 "vendor": "Microsoft Office"},
    {"sub": "GAdm.Afi",  "name": "Software Administrativo y Contable",    "vendor": "Loggro Pymes"},
    # ── G.Op — Seguros ─────────────────────────────────────────────────────
    {"sub": "GAdm.Seg",  "name": "Todo riesgo Oficina Central",           "vendor": "Seguros Generales SURA"},
    {"sub": "GAdm.Seg",  "name": "Pyme Protegida",                        "vendor": "Seguros Generales SURA"},
    {"sub": "GAdm.Seg",  "name": "Seguro de Vida (Crédito Sempli)",       "vendor": "Sempli"},
    # ── G.Op — Servicios (Adm) ─────────────────────────────────────────────
    {"sub": "GAdm.Ser",  "name": "Servicios públicos",                    "vendor": "EPM"},
    {"sub": "GAdm.Ser",  "name": "Celular Administrativo",                "vendor": "Claro"},
    {"sub": "GAdm.Ser",  "name": "Internet",                              "vendor": "Movistar"},
    # ── G.Op — Mantenimiento ───────────────────────────────────────────────
    {"sub": "GAdm.Man",  "name": "Construcciones y edificaciones",        "vendor": "Varios"},
    {"sub": "GAdm.Man",  "name": "Equipo de computación y comunicación",  "vendor": "Varios"},
    # ── G.Op — Diversos (Adm) ──────────────────────────────────────────────
    {"sub": "GAdm.Div",  "name": "Taxis, buses y peajes",                 "vendor": "Varios"},
    {"sub": "GAdm.Div",  "name": "Elementos de aseo y cafetería",         "vendor": "Almacenes D1"},
    {"sub": "GAdm.Div",  "name": "Útiles, papelería y fotocopias",        "vendor": "Papelería Taiwan"},
    {"sub": "GAdm.Div",  "name": "Servicios de aseo y vigilancia",        "vendor": "Gilma Gloria - Elkin Ceballos"},
    # ── G.Op — Gastos de Ventas — Honorarios Directivos ────────────────────
    {"sub": "GVen.Dir",  "name": "Honorarios Directivo Comercial",        "vendor": "Simón Cuesta Londoño"},
    {"sub": "GVen.Dir",  "name": "Honorarios Directivo Marca",            "vendor": "Juan Pablo Castaño Ramirez"},
    # ── G.Op — Gastos de Ventas — Externos ─────────────────────────────────
    {"sub": "GVen.Ext",  "name": "Asesoría publicitaria",                 "vendor": ""},
    {"sub": "GVen.Ext",  "name": "Otros",                                 "vendor": ""},
    # ── G.Op — Gastos de Ventas — Afiliaciones ─────────────────────────────
    {"sub": "GVen.Afi",  "name": "Afiliaciones y sostenimiento - Suscripciones", "vendor": "Pipedrive"},
    # ── G.Op — Gastos de Ventas — Servicios ────────────────────────────────
    {"sub": "GVen.Ser",  "name": "Teléfono",                              "vendor": "Movistar"},
    {"sub": "GVen.Ser",  "name": "Servicios de publicidad",               "vendor": "Google y Facebook Ads"},
    # ── G.Op — Gastos de Ventas — Viaje ────────────────────────────────────
    {"sub": "GVen.Via",  "name": "Pasajes terrestres",                    "vendor": "Varios"},
    # ── G.Op — Gastos de Ventas — Relacionamiento ──────────────────────────
    {"sub": "GVen.Rel",  "name": "Gastos de representación y relaciones", "vendor": "Varios"},
    # ── G.Op — Gastos de Ventas — Diversos ─────────────────────────────────
    {"sub": "GVen.Div",  "name": "Transporte, peajes y viáticos",         "vendor": "General"},
    # ── G.NoOp — Bancarios ─────────────────────────────────────────────────
    {"sub": "GFin.Ban",  "name": "Gastos de sucursal",                    "vendor": "Bancolombia"},
    {"sub": "GFin.Ban",  "name": "Cuotas de manejo - Cuentas Ahorros",    "vendor": "Bancolombia"},
    {"sub": "GFin.Ban",  "name": "Comisiones Pagos de Nómina y Proveedores", "vendor": "Bancolombia"},
    {"sub": "GFin.Ban",  "name": "Obligaciones Financieras Intereses",    "vendor": "Varios"},
    {"sub": "GFin.Ban",  "name": "Obligaciones Financieras - Cuota Mensual", "vendor": "Varios"},
    # ── Impuestos ──────────────────────────────────────────────────────────
    {"sub": "Imp.Ren",   "name": "Impuesto a la Renta",                   "vendor": "DIAN"},
    {"sub": "Imp.ICA",   "name": "Industria y comercio (10*1000/ventas)", "vendor": "Hacienda Municipal"},
    {"sub": "Imp.4x1",   "name": "Impuesto a la Transacción (4*1000/ventas)", "vendor": "Hacienda"},
]


class Command(BaseCommand):
    help = "Carga la estructura de categorías, subcategorías y conceptos de gasto de CNTXT."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Elimina todos los registros existentes antes de cargar.",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            OperationalExpenseType.objects.all().delete()
            ExpenseSubCategory.objects.all().delete()
            ExpenseCategory.objects.all().delete()
            self.stdout.write(self.style.WARNING("Registros existentes eliminados."))

        # ── Categorías ──────────────────────────────────────────────────────
        cat_map = {}
        for data in CATEGORIES:
            obj, created = ExpenseCategory.objects.update_or_create(
                code=data["code"],
                defaults={"name": data["name"], "category_type": data["type"], "is_active": True},
            )
            cat_map[data["code"]] = obj
            label = "✓ creada" if created else "↺ actualizada"
            self.stdout.write(f"  Categoría {label}: {obj}")

        # ── Subcategorías ───────────────────────────────────────────────────
        sub_map = {}
        for data in SUBCATEGORIES:
            cat = cat_map[data["cat"]]
            obj, created = ExpenseSubCategory.objects.update_or_create(
                category=cat,
                code=data["code"],
                defaults={"name": data["name"], "is_active": True},
            )
            sub_map[data["code"]] = obj
            label = "✓ creada" if created else "↺ actualizada"
            self.stdout.write(f"    Subcategoría {label}: {obj}")

        # ── Conceptos ───────────────────────────────────────────────────────
        created_c = updated_c = 0
        for data in CONCEPTS:
            sub = sub_map[data["sub"]]
            obj, created = OperationalExpenseType.objects.get_or_create(
                subcategory=sub,
                name=data["name"],
                vendor=data["vendor"],
                defaults={"is_active": True},
            )
            if created:
                created_c += 1
            else:
                updated_c += 1

        self.stdout.write(self.style.SUCCESS(
            f"\n✅ Listo — {len(CATEGORIES)} categorías · {len(SUBCATEGORIES)} subcategorías · "
            f"{created_c} conceptos creados · {updated_c} ya existían."
        ))
