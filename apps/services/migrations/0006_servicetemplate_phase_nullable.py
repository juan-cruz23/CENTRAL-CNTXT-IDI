from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("services", "0005_add_hardware_software"),
    ]

    operations = [
        migrations.AlterField(
            model_name="servicetemplate",
            name="phase",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="service_templates",
                to="services.projectphase",
                verbose_name="fase",
            ),
        ),
    ]
