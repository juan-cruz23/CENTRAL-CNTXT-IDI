"""Add M2M operative_lines to ServiceSubCategory + data migration.

The legacy single FK `operative_line` is preserved temporarily (renamed
related_name to `subcategories_legacy`) so we don't lose data. New code
uses `operative_lines` (M2M). Forward data migration copies the FK value
into the M2M for every existing row.
"""

import django.db.models.deletion
from django.db import migrations, models


def copy_fk_to_m2m(apps, schema_editor):
    """Forward: copy each subcategory.operative_line into the new M2M set."""
    ServiceSubCategory = apps.get_model("services", "ServiceSubCategory")
    for sub in ServiceSubCategory.objects.all():
        if sub.operative_line_id:
            sub.operative_lines.add(sub.operative_line_id)


def restore_m2m_to_fk(apps, schema_editor):
    """Reverse: pick first M2M line and put it back in the FK."""
    ServiceSubCategory = apps.get_model("services", "ServiceSubCategory")
    for sub in ServiceSubCategory.objects.all():
        first = sub.operative_lines.first()
        if first and not sub.operative_line_id:
            sub.operative_line_id = first.id
            sub.save(update_fields=["operative_line"])


class Migration(migrations.Migration):

    dependencies = [
        ("organizations", "0001_initial"),
        ("services", "0023_alter_deliverable_name_alter_keyactivity_name_and_more"),
    ]

    operations = [
        # 1. Add the new M2M field
        migrations.AddField(
            model_name="servicesubcategory",
            name="operative_lines",
            field=models.ManyToManyField(
                blank=True,
                help_text="Una subcategoría puede pertenecer a varias líneas operativas.",
                related_name="subcategories",
                to="organizations.operativeline",
                verbose_name="líneas operativas",
            ),
        ),
        # 2. Rename related_name on legacy FK to avoid clash with new M2M related_name
        migrations.AlterField(
            model_name="servicesubcategory",
            name="operative_line",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="subcategories_legacy",
                to="organizations.operativeline",
                verbose_name="línea operativa (legado)",
            ),
        ),
        # 3. Copy legacy FK values into the new M2M set
        migrations.RunPython(copy_fk_to_m2m, restore_m2m_to_fk),
    ]
