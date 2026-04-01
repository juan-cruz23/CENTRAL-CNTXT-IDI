from django.db import migrations

COLOMBIA_MUNICIPALITIES = [
    # (departamento, municipio)
    ("Amazonas", "Leticia"), ("Amazonas", "Puerto Nariño"),
    ("Antioquia", "Medellín"), ("Antioquia", "Bello"), ("Antioquia", "Envigado"),
    ("Antioquia", "Itagüí"), ("Antioquia", "Rionegro"), ("Antioquia", "Apartadó"),
    ("Antioquia", "Turbo"), ("Antioquia", "Caucasia"),
    ("Arauca", "Arauca"), ("Arauca", "Saravena"),
    ("Atlántico", "Barranquilla"), ("Atlántico", "Soledad"), ("Atlántico", "Malambo"),
    ("Bolívar", "Cartagena"), ("Bolívar", "Magangué"), ("Bolívar", "El Carmen de Bolívar"),
    ("Boyacá", "Tunja"), ("Boyacá", "Duitama"), ("Boyacá", "Sogamoso"), ("Boyacá", "Chiquinquirá"),
    ("Caldas", "Manizales"), ("Caldas", "La Dorada"), ("Caldas", "Chinchiná"),
    ("Caquetá", "Florencia"), ("Caquetá", "San Vicente del Caguán"),
    ("Casanare", "Yopal"), ("Casanare", "Aguazul"),
    ("Cauca", "Popayán"), ("Cauca", "Santander de Quilichao"), ("Cauca", "Puerto Tejada"),
    ("Cesar", "Valledupar"), ("Cesar", "Aguachica"), ("Cesar", "Codazzi"),
    ("Chocó", "Quibdó"), ("Chocó", "Istmina"),
    ("Córdoba", "Montería"), ("Córdoba", "Lorica"), ("Córdoba", "Sahagún"),
    ("Cundinamarca", "Soacha"), ("Cundinamarca", "Fusagasugá"), ("Cundinamarca", "Zipaquirá"),
    ("Cundinamarca", "Facatativá"), ("Cundinamarca", "Chía"), ("Cundinamarca", "Mosquera"),
    ("Cundinamarca", "Madrid"), ("Cundinamarca", "Girardot"),
    ("Bogotá D.C.", "Bogotá D.C."),
    ("Guainía", "Inírida"),
    ("Guaviare", "San José del Guaviare"),
    ("Huila", "Neiva"), ("Huila", "Pitalito"), ("Huila", "Garzón"),
    ("La Guajira", "Riohacha"), ("La Guajira", "Maicao"), ("La Guajira", "Uribia"),
    ("Magdalena", "Santa Marta"), ("Magdalena", "Ciénaga"), ("Magdalena", "Fundación"),
    ("Meta", "Villavicencio"), ("Meta", "Acacías"), ("Meta", "Granada"),
    ("Nariño", "Pasto"), ("Nariño", "Tumaco"), ("Nariño", "Ipiales"),
    ("Norte de Santander", "Cúcuta"), ("Norte de Santander", "Ocaña"), ("Norte de Santander", "Pamplona"),
    ("Putumayo", "Mocoa"), ("Putumayo", "Puerto Asís"),
    ("Quindío", "Armenia"), ("Quindío", "Calarcá"),
    ("Risaralda", "Pereira"), ("Risaralda", "Dosquebradas"), ("Risaralda", "Santa Rosa de Cabal"),
    ("San Andrés y Providencia", "San Andrés"), ("San Andrés y Providencia", "Providencia"),
    ("Santander", "Bucaramanga"), ("Santander", "Floridablanca"), ("Santander", "Girón"),
    ("Santander", "Piedecuesta"), ("Santander", "Barrancabermeja"),
    ("Sucre", "Sincelejo"), ("Sucre", "Corozal"),
    ("Tolima", "Ibagué"), ("Tolima", "Espinal"), ("Tolima", "Melgar"),
    ("Valle del Cauca", "Cali"), ("Valle del Cauca", "Palmira"), ("Valle del Cauca", "Buenaventura"),
    ("Valle del Cauca", "Tuluá"), ("Valle del Cauca", "Buga"), ("Valle del Cauca", "Cartago"),
    ("Vaupés", "Mitú"),
    ("Vichada", "Puerto Carreño"),
]


def load_colombia(apps, schema_editor):
    Country = apps.get_model("geography", "Country")
    Municipality = apps.get_model("geography", "Municipality")
    colombia = Country.objects.create(name="Colombia", iso_code="CO")
    Municipality.objects.bulk_create([
        Municipality(name=municipio, department=depto, country=colombia)
        for depto, municipio in COLOMBIA_MUNICIPALITIES
    ])


def unload_colombia(apps, schema_editor):
    Country = apps.get_model("geography", "Country")
    Country.objects.filter(iso_code="CO").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("geography", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_colombia, unload_colombia),
    ]
