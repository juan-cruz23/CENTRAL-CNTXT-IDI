"""
Data migration: Copy all Client records to ThirdParty and link Projects.

Steps:
1. For each Client → create ThirdParty with relationship_type=CLIENTE
2. For each Project with a client → set third_party via legacy_client_id
"""

from django.db import migrations


def migrate_clients_forward(apps, schema_editor):
    Client = apps.get_model("projects", "Client")
    ThirdParty = apps.get_model("terceros", "ThirdParty")
    Project = apps.get_model("projects", "Project")

    # Step 1: Copy Client → ThirdParty
    for client in Client.objects.all():
        ThirdParty.objects.create(
            name=client.name,
            company=client.company or "",
            relationship_type="CLIENTE",
            client_category=client.category or "",
            email=client.email or "",
            phone=client.phone or "",
            notes=client.notes or "",
            is_active=True,
            legacy_client_id=client.pk,
        )

    # Step 2: Link Project.third_party from Project.client
    for tp in ThirdParty.objects.filter(legacy_client_id__isnull=False):
        Project.objects.filter(client_id=tp.legacy_client_id).update(
            third_party=tp
        )


def migrate_clients_reverse(apps, schema_editor):
    ThirdParty = apps.get_model("terceros", "ThirdParty")
    Project = apps.get_model("projects", "Project")

    # Unlink projects
    Project.objects.filter(third_party__isnull=False).update(third_party=None)

    # Delete migrated ThirdParty records (only those from Client)
    ThirdParty.objects.filter(legacy_client_id__isnull=False).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("terceros", "0001_initial"),
        ("projects", "0002_project_third_party"),
    ]

    operations = [
        migrations.RunPython(
            migrate_clients_forward,
            migrate_clients_reverse,
        ),
    ]
