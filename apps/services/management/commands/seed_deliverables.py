"""
Management command: seed_deliverables
Carga los entregables de la hoja D.sign DATA del archivo
05. Services_05.25.xlsm en el modelo Deliverable.

Idempotente: usa get_or_create. Se puede ejecutar múltiples veces
sin duplicar registros.

Uso:
    python manage.py seed_deliverables
"""

import os

from django.core.management.base import BaseCommand


EXCEL_PATH = os.path.join(
    os.path.dirname(__file__),
    "..", "..", "..", "..", "..",
    "Documentacion", "05. Services_05.25.xlsm",
)

# Mapeo: código de servicio → lista de (entregable, unidad)
# Extraído de la hoja D.sign DATA (columnas G y H), filas únicas por entregable.
DELIVERABLES_DATA = [
    ("D0.1", "Canales de comunicación y almacenamiento", "Proyecto", 1),
    ("D0.1", "Programación", "Proyecto", 2),
    ("D0.1", "Diagnóstico Inicial del proyecto", "Proyecto", 3),
    ("D0.1", "Encuesta formato google forms", "Proyecto", 4),
    ("D0.2", "Construcción de Concepto", "Análisis", 1),
    ("D0.2", "Estudio contextual", "Proyecto", 2),
    ("D0.3", "Presentación de desarrollo arquitectónico", "Proyecto", 1),
    ("D0.3", "Entrega", "Proyecto", 2),
    ("D1.1", "Modelo Tridimensional, Viewer 360 Escala Urbana", "Proyecto", 1),
    ("D1.2", "Modelado Tridimensional Viewer 360, zona complementaria", "100m2", 1),
    ("D1.5", "Planimetría Arquitectónica, Zona complementaria", "100m2", 1),
    ("D1.6", "Planimetría arquitectónica escala variable según requerimiento.", "100m2", 1),
    ("D1.7", "Modelo Tridimensional, detalle Escala Urbana", "1 ha", 1),
    ("D1.8", "Modelado Tridimensional Viewer 360 Zona complementaria", "Und", 1),
    ("D1.10", "Planimetría Arquitectónica del Urbanismo", "15 ha", 1),
    ("D1.11", "Planimetría Arquitectónica Elementos Complementarios", "Und", 1),
    ("D1.12", "Planimetría Arquitectónica Edificación", "100m2", 1),
    ("D1.13", "Especificaciones del Urbanismo", "15 ha", 1),
    ("D1.14", "Especificaciones de Elemento Complementario", "Und", 1),
    ("D1.15", "Especificaciones", "Und", 1),
    ("D1.16", "Modelo Tridimensional a través de LINK en nube.", "500 m² - 1000 m²", 1),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Borde de losa)", "500 m² - 1000 m²", 1),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Pisos)", "500 m² - 1000 m²", 2),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Cubiertas y pérgolas)", "500 m² - 1000 m²", 3),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Acabados en muros)", "500 m² - 1000 m²", 4),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Iluminación)", "500 m² - 1000 m²", 5),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Cielos)", "500 m² - 1000 m²", 6),
    ("D1.18", "Planimetría Arquitectónica de Detalle (Puertas y Ventanas)", "500 m² - 1000 m²", 7),
    ("D1.19", "Planimetría Arquitectónica de Detalle (Carpintería)", "1 m² - 200 m²", 1),
    ("D1.20", "Especificaciones de proyecto", "500 m² - 1000 m²", 1),
    ("D1.21", "Especificaciones de Edificación", "1 m² - 200 m²", 1),
    ("D1.22", "Plano", "10ha", 1),
    ("D1.23", "Manual", "1", 1),
    ("D1.24", "Modelo Base + Topografía", "1 Proyecto", 1),
    ("D2.4", "Planimetría Arquitectónica de Edificación en Altura", "100m2", 1),
    ("D2.5", "Especificaciones de Edificación en Altura", "200m2", 1),
    ("D3.3", "Especificaciones de Vivienda Campestre", "100m2", 1),
    ("D3.5", "Planimetría Arquitectónica de Vivienda Campestre", "100m2", 1),
    ("D3.6", "Experiencia de replanteo de espacios de la vivienda 1:1 en lote", "1", 1),
    ("D3.10", "Ficha de lote", "Documento PDF", 1),
    ("D4.1", "Cabida Preliminar", "Proyecto", 1),
    ("D4.1", "Presentación de concepto espacial, determinantes y cabida", "Proyecto", 2),
    ("D4.1", "Modelo Tridimensional del Estado Preliminar", "Proyecto", 3),
    ("D4.1", "Paquete de planos Arquitectónicos del estado preliminar", "Proyecto", 4),
    ("D4.1", "Presentación de conceptualización e ideación general", "Proyecto", 5),
    ("D4.2", "Paquete de planimetría técnica de stand + Viewer 360", "Proyecto", 1),
    ("D4.3", "Presupuesto", "Proyecto", 1),
    ("D4.3", "Extracción de cantidades de obra", "Proyecto", 2),
    ("D6.5", "Especificaciones, experiencia de compra y cantidades de obra", "Und", 1),
    ("D6.6", "Planimetría", "50m2", 1),
    ("D6.6", "Viewer 360", "50m2", 2),
    ("D6.6", "3 Renders Interiores", "50m2", 3),
    # ── Servicios adicionales ────────────────────────────────────────────────
    ("D1.3", "Modelo Tridimensional a través de LINK en nube.", "100m2", 1),
    ("D1.4", "Planimetría Arquitectónica del Urbanismo", "15 ha", 1),
    ("D1.9", "Modelo Tridimensional a través de LINK en nube.", "100m2", 1),
    ("D1.9", "Modelo Tridimensional a través de LINK en nube.", "Und", 2),
    ("D1.17", "Modelo Tridimensional a través de LINK en nube.", "1 m² - 200 m²", 1),
    ("D1.25", "Modelado Tridimensional Viewer 360 Zona complementaria", "Und", 1),
    ("D1.26", "Planimetría Arquitectónica Elementos Complementarios", "Und", 1),
    ("D2.1", "Modelo Tridimensional a través de LINK en nube.", "200m2", 1),
    ("D2.2", "Planimetría arquitectónica escala variable según requerimiento.", "200m2", 1),
    ("D2.2", "Planimetría arquitectónica escala variable según requerimiento.", "Und", 2),
    ("D2.3", "Modelo Tridimensional a través de LINK en nube.", "100m2", 1),
    ("D2.3", "Modelo Tridimensional a través de LINK en nube.", "Und", 2),
    ("D2.6", "Modelo Tridimensional a través de LINK en nube.", "1 m² - 200 m²", 1),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Borde de losa)", "1 m² - 200 m²", 1),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Pisos)", "1 m² - 200 m²", 2),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Cubiertas y pérgolas)", "1 m² - 200 m²", 3),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Acabados en muros)", "1 m² - 200 m²", 4),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Iluminación)", "1 m² - 200 m²", 5),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Cielos)", "1 m² - 200 m²", 6),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Puertas y Ventanas)", "1 m² - 200 m²", 7),
    ("D2.7", "Planimetría Arquitectónica de Detalle (Carpintería)", "1 m² - 200 m²", 8),
    ("D2.8", "Especificaciones de Edificación", "1 m² - 200 m²", 1),
    ("D3.1", "Modelo Tridimensional a través de LINK en nube.", "100m2", 1),
    ("D3.2", "Planimetría arquitectónica escala variable según requerimiento.", "100m2", 1),
    ("D3.2", "Planimetría arquitectónica escala variable según requerimiento.", "Und", 2),
    ("D3.4", "Modelo Tridimensional a través de LINK en nube.", "100m2", 1),
    ("D3.4", "Modelo Tridimensional a través de LINK en nube.", "Und", 2),
    ("D3.7", "Modelo Tridimensional a través de LINK en nube.", "1 m² - 200 m²", 1),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Borde de losa)", "1 m² - 200 m²", 1),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Pisos)", "1 m² - 200 m²", 2),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Cubiertas y pérgolas)", "1 m² - 200 m²", 3),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Acabados en muros)", "1 m² - 200 m²", 4),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Iluminación)", "1 m² - 200 m²", 5),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Cielos)", "1 m² - 200 m²", 6),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Puertas y Ventanas)", "1 m² - 200 m²", 7),
    ("D3.8", "Planimetría Arquitectónica de Detalle (Carpintería)", "1 m² - 200 m²", 8),
    ("D3.9", "Especificaciones de Edificación", "1 m² - 200 m²", 1),
    ("D3.11", "Ficha de lote", "Documento PDF", 1),
    ("D6.1", "Cabida Preliminar", "Proyecto", 1),
    ("D6.1", "Presentación de concepto espacial, determinantes y cabida", "100m2", 2),
    ("D6.1", "Modelo Tridimensional del Estado Preliminar", "10m2", 3),
    ("D6.1", "Paquete de planos Arquitectónicos del estado preliminar", "10m2", 4),
    ("D6.1", "Paquete de planos Arquitectónicos del estado preliminar", "Proyecto", 5),
    ("D6.2", "Presentación de conceptualización e ideación general", "Proyecto", 1),
    ("D6.2", "Presentación de conceptualización e ideación general", "100m2", 2),
    ("D6.2", "Presentación de conceptualización e ideación general", "Imagen", 3),
    ("D6.2", "Presentación de conceptualización e ideación general", "Referentes", 4),
    ("D6.3", "Modelo Tridimensional a través de LINK en nube.", "1 m² - 200 m²", 1),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Pisos)", "1 m² - 200 m²", 1),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Cubiertas y pérgolas)", "1 m² - 200 m²", 2),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Acabados en muros)", "1 m² - 200 m²", 3),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Iluminación)", "1 m² - 200 m²", 4),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Cielos)", "1 m² - 200 m²", 5),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Puertas y Ventanas)", "1 m² - 200 m²", 6),
    ("D6.4", "Planimetría Arquitectónica de Detalle (Carpintería)", "1 m² - 200 m²", 7),
    ("D6.7", "Presentación de concepto espacial, determinantes y cabida", "PDF", 1),
    ("D6.7", "Cabida Preliminar", "PDF", 2),
    ("D6.7", "Modelo Tridimensional del Estado Preliminar", "PDF", 3),
    ("D6.7", "Planimetría", "PDF", 4),
    ("D6.7", "Paquete de planos Arquitectónicos del estado preliminar", "PDF", 5),
    ("D6.7", "Viewer 360", "PDF", 6),
    ("D6.7", "3 Renders Interiores", "PDF", 7),
    ("D7.1", "Modelo Tridimensional a través de LINK en nube.", "100m2", 1),
    ("D7.2", "Planimetría arquitectónica escala variable según requerimiento.", "100m2", 1),
]


class Command(BaseCommand):
    help = "Carga entregables de servicios D.sign desde el Excel maestro."

    def handle(self, *args, **options):
        from apps.services.models import Deliverable, ServiceTemplate

        created_count = 0
        skipped_count = 0
        missing_services = set()

        for code, name, unit, order in DELIVERABLES_DATA:
            try:
                service = ServiceTemplate.objects.get(code=code)
            except ServiceTemplate.DoesNotExist:
                missing_services.add(code)
                skipped_count += 1
                continue

            _, created = Deliverable.objects.get_or_create(
                service_template=service,
                name=name,
                defaults={"unit": unit, "order": order},
            )
            if created:
                created_count += 1

        if missing_services:
            self.stdout.write(
                self.style.WARNING(
                    f"  Servicios no encontrados (omitidos): {', '.join(sorted(missing_services))}"
                )
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"✓ Entregables: {created_count} creados, {skipped_count} omitidos por servicio faltante."
            )
        )
