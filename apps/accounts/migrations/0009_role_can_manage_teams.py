from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0008_add_badges"),
    ]

    operations = [
        migrations.AddField(
            model_name="role",
            name="can_manage_teams",
            field=models.BooleanField(
                default=False,
                verbose_name="puede gestionar equipos semanales",
                help_text="Puede crear y editar equipos de trabajo semanales por proyecto.",
            ),
        ),
    ]
