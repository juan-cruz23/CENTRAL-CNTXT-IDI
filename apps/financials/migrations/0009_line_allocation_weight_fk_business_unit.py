from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("financials", "0008_add_line_allocation_weight"),
        ("organizations", "0001_initial"),
    ]

    operations = [
        # 1. Clear existing unique_together that references operative_line
        migrations.AlterUniqueTogether(
            name="lineallocationweight",
            unique_together=set(),
        ),
        # 2. Remove old FK
        migrations.RemoveField(
            model_name="lineallocationweight",
            name="operative_line",
        ),
        # 3. Add new FK
        migrations.AddField(
            model_name="lineallocationweight",
            name="business_unit",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="allocation_weights",
                to="organizations.businessunit",
                verbose_name="unidad de negocio",
                default=1,
            ),
            preserve_default=False,
        ),
        # 4. Set new unique_together
        migrations.AlterUniqueTogether(
            name="lineallocationweight",
            unique_together={("quarter", "business_unit")},
        ),
        migrations.AlterModelOptions(
            name="lineallocationweight",
            options={
                "ordering": ["quarter", "business_unit__code"],
                "verbose_name": "peso de unidad de negocio por trimestre",
                "verbose_name_plural": "pesos de unidades de negocio por trimestre",
            },
        ),
    ]
