"""
Seed data for Central Contexto 2.0.
Seeds: Roles, Organizational Systems, Business Units, Operative Lines,
Colombian Holidays 2025-2027, and initial admin user.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Seed initial data for Central Contexto 2.0"

    def add_arguments(self, parser):
        parser.add_argument("--flush", action="store_true", help="Delete existing seed data before inserting")

    def handle(self, *args, **options):
        if options["flush"]:
            self.stdout.write("Flushing existing seed data...")
            self._flush()

        self.stdout.write("Seeding roles...")
        self._seed_roles()
        self.stdout.write("Seeding organizational systems...")
        self._seed_systems()
        self.stdout.write("Seeding business units and operative lines...")
        self._seed_business_units()
        self.stdout.write("Seeding Colombian holidays 2025-2027...")
        self._seed_holidays()
        self.stdout.write("Seeding admin user...")
        self._seed_admin()
        self.stdout.write(self.style.SUCCESS("Seed data loaded successfully!"))

    def _flush(self):
        from apps.accounts.models import Role
        from apps.organizations.models import OrganizationalSystem, BusinessUnit, OperativeLine
        from apps.financials.models import ColombianHoliday
        ColombianHoliday.objects.all().delete()
        OperativeLine.objects.all().delete()
        BusinessUnit.objects.all().delete()
        OrganizationalSystem.objects.all().delete()
        Role.objects.all().delete()

    def _seed_roles(self):
        from apps.accounts.models import Role
        roles = [
            {"code": "LA", "name": "Líder de Arquitectura", "default_hourly_rate": 85000, "description": "Lidera proyectos de diseño arquitectónico"},
            {"code": "INT", "name": "Interiorista", "default_hourly_rate": 75000, "description": "Diseño de interiores y conceptualización"},
            {"code": "VS", "name": "Visualizador Senior", "default_hourly_rate": 70000, "description": "Visualización 3D y renders de alta calidad"},
            {"code": "VL", "name": "Visualizador", "default_hourly_rate": 60000, "description": "Modelado 3D y visualización"},
            {"code": "DM", "name": "Diseñador Multimedia", "default_hourly_rate": 55000, "description": "Diseño gráfico y multimedia"},
            {"code": "AI_I", "name": "Asistente de Inteligencia I", "default_hourly_rate": 45000, "description": "Asistencia en investigación y análisis"},
            {"code": "AI_M", "name": "Asistente de Inteligencia M", "default_hourly_rate": 45000, "description": "Asistencia en modelado e inteligencia"},
        ]
        for role_data in roles:
            Role.objects.update_or_create(code=role_data["code"], defaults=role_data)
        self.stdout.write(f"  Created/updated {len(roles)} roles")

    def _seed_systems(self):
        from apps.organizations.models import OrganizationalSystem
        systems = [
            {"code": "NEO", "name": "NEO - Sistema de Dirección", "analogy": "Cerebro", "description": "Dirección estratégica y toma de decisiones de alto nivel"},
            {"code": "IDI", "name": "IDI - Sistema de Innovación", "analogy": "Sistema Nervioso", "description": "Investigación, desarrollo e innovación"},
            {"code": "RED", "name": "RED - Sistema de Conexiones", "analogy": "Sistema Circulatorio", "description": "Comunicación, relaciones y networking"},
            {"code": "CASH", "name": "CASH - Sistema Financiero", "analogy": "Sistema Digestivo", "description": "Gestión financiera, facturación y cobros"},
            {"code": "CORE", "name": "CORE - Sistema Operativo", "analogy": "Músculos y Huesos", "description": "Operación principal, ejecución de proyectos"},
            {"code": "BONES", "name": "BONES - Sistema Estructural", "analogy": "Esqueleto", "description": "Infraestructura, procesos y estructura organizacional"},
        ]
        for sys_data in systems:
            OrganizationalSystem.objects.update_or_create(code=sys_data["code"], defaults=sys_data)
        self.stdout.write(f"  Created/updated {len(systems)} systems")

    def _seed_business_units(self):
        from apps.organizations.models import BusinessUnit, OperativeLine

        # Business Units
        made, _ = BusinessUnit.objects.update_or_create(
            code="MADE", defaults={"name": "MADE - Estudio de Diseño", "description": "Unidad principal de diseño arquitectónico y visual"}
        )
        select, _ = BusinessUnit.objects.update_or_create(
            code="SELECT", defaults={"name": "SELECT - Servicios Especializados", "description": "Servicios especializados y consultoría"}
        )

        # Operative Lines
        lines = [
            {"code": "DV", "name": "Diseño y Visual", "business_unit": made, "description": "Diseño arquitectónico y visualización"},
            {"code": "VIS", "name": "Visualización", "business_unit": made, "description": "Renders, recorridos virtuales y visualización 3D"},
            {"code": "TV", "name": "Tech Ventas", "business_unit": select, "description": "Tecnología aplicada a ventas inmobiliarias"},
            {"code": "IF", "name": "Intel Financiera", "business_unit": select, "description": "Inteligencia financiera y análisis de datos"},
        ]
        for line_data in lines:
            OperativeLine.objects.update_or_create(code=line_data["code"], defaults=line_data)
        self.stdout.write(f"  Created/updated 2 business units and {len(lines)} operative lines")

    def _seed_holidays(self):
        from apps.financials.models import ColombianHoliday
        from datetime import date

        holidays = [
            # 2025
            (date(2025, 1, 1), "Año Nuevo"),
            (date(2025, 1, 6), "Día de los Reyes Magos"),
            (date(2025, 3, 24), "Día de San José"),
            (date(2025, 4, 17), "Jueves Santo"),
            (date(2025, 4, 18), "Viernes Santo"),
            (date(2025, 5, 1), "Día del Trabajo"),
            (date(2025, 6, 2), "Ascensión del Señor"),
            (date(2025, 6, 23), "Corpus Christi"),
            (date(2025, 6, 30), "Sagrado Corazón de Jesús"),
            (date(2025, 7, 20), "Día de la Independencia"),
            (date(2025, 8, 7), "Batalla de Boyacá"),
            (date(2025, 8, 18), "La Asunción de la Virgen"),
            (date(2025, 10, 13), "Día de la Raza"),
            (date(2025, 11, 3), "Todos los Santos"),
            (date(2025, 11, 17), "Independencia de Cartagena"),
            (date(2025, 12, 8), "Día de la Inmaculada Concepción"),
            (date(2025, 12, 25), "Navidad"),
            # 2026
            (date(2026, 1, 1), "Año Nuevo"),
            (date(2026, 1, 12), "Día de los Reyes Magos"),
            (date(2026, 3, 23), "Día de San José"),
            (date(2026, 4, 2), "Jueves Santo"),
            (date(2026, 4, 3), "Viernes Santo"),
            (date(2026, 5, 1), "Día del Trabajo"),
            (date(2026, 5, 18), "Ascensión del Señor"),
            (date(2026, 6, 8), "Corpus Christi"),
            (date(2026, 6, 15), "Sagrado Corazón de Jesús"),
            (date(2026, 6, 29), "San Pedro y San Pablo"),
            (date(2026, 7, 20), "Día de la Independencia"),
            (date(2026, 8, 7), "Batalla de Boyacá"),
            (date(2026, 8, 17), "La Asunción de la Virgen"),
            (date(2026, 10, 12), "Día de la Raza"),
            (date(2026, 11, 2), "Todos los Santos"),
            (date(2026, 11, 16), "Independencia de Cartagena"),
            (date(2026, 12, 8), "Día de la Inmaculada Concepción"),
            (date(2026, 12, 25), "Navidad"),
            # 2027
            (date(2027, 1, 1), "Año Nuevo"),
            (date(2027, 1, 11), "Día de los Reyes Magos"),
            (date(2027, 3, 22), "Día de San José"),
            (date(2027, 3, 25), "Jueves Santo"),
            (date(2027, 3, 26), "Viernes Santo"),
            (date(2027, 5, 1), "Día del Trabajo"),
            (date(2027, 5, 10), "Ascensión del Señor"),
            (date(2027, 5, 31), "Corpus Christi"),
            (date(2027, 6, 7), "Sagrado Corazón de Jesús"),
            (date(2027, 6, 28), "San Pedro y San Pablo"),
            (date(2027, 7, 20), "Día de la Independencia"),
            (date(2027, 8, 7), "Batalla de Boyacá"),
            (date(2027, 8, 16), "La Asunción de la Virgen"),
            (date(2027, 10, 18), "Día de la Raza"),
            (date(2027, 11, 1), "Todos los Santos"),
            (date(2027, 11, 15), "Independencia de Cartagena"),
            (date(2027, 12, 8), "Día de la Inmaculada Concepción"),
            (date(2027, 12, 25), "Navidad"),
        ]
        count = 0
        for holiday_date, name in holidays:
            _, created = ColombianHoliday.objects.update_or_create(date=holiday_date, defaults={"name": name})
            if created:
                count += 1
        self.stdout.write(f"  Created {count} new holidays (total: {len(holidays)})")

    def _seed_admin(self):
        if not User.objects.filter(username="admin").exists():
            User.objects.create_superuser(
                username="admin",
                email="admin@cntxt.com.co",
                password="admin123",
                first_name="Admin",
                last_name="CNTXT",
            )
            self.stdout.write("  Created admin user (admin/admin123)")
        else:
            self.stdout.write("  Admin user already exists")
