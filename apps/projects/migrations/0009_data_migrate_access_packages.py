from django.db import migrations


PACKAGES = [
    {"code": "ESSENTIAL", "name": "Essential", "description": "Acceso básico a la plataforma. Incluye gestión de proyectos, cronograma y seguimiento operativo."},
    {"code": "ADVANCED", "name": "Advanced", "description": "Acceso intermedio. Incluye todo Essential más reportes financieros básicos y gestión de documentos."},
    {"code": "PREMIUM", "name": "Premium", "description": "Acceso completo. Incluye todo Advanced más métricas, satisfacción del cliente y alertas automáticas."},
    {"code": "PREMIUM_ADVANCED", "name": "Premium Advanced", "description": "Acceso máximo. Incluye todo Premium más capacidad, análisis de rentabilidad en tiempo real e integraciones externas."},
]

# Mapeo de access_type legacy → código de paquete
LEGACY_MAP = {
    "PREMIUM": "PREMIUM",
    "STANDARD": "ESSENTIAL",
}


def create_packages_and_migrate(apps, schema_editor):
    AccessPackage = apps.get_model("accounts", "AccessPackage")
    Project = apps.get_model("projects", "Project")

    # Crear paquetes base
    for pkg in PACKAGES:
        AccessPackage.objects.get_or_create(code=pkg["code"], defaults={"name": pkg["name"], "description": pkg["description"]})

    # Asignar paquete a proyectos existentes según access_type legacy
    for project in Project.objects.all():
        pkg_code = LEGACY_MAP.get(project.access_type, "ESSENTIAL")
        pkg = AccessPackage.objects.filter(code=pkg_code).first()
        if pkg:
            project.access_package = pkg
            project.save(update_fields=["access_package"])


def reverse_migrate(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0008_add_access_package_fk"),
        ("accounts", "0004_add_access_package"),
    ]

    operations = [
        migrations.RunPython(create_packages_and_migrate, reverse_migrate),
    ]
