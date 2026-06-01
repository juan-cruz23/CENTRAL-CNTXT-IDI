import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="WeeklyTeam",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("project_name", models.CharField(max_length=200, verbose_name="proyecto", help_text="Nombre del proyecto o contexto del equipo.")),
                ("week_number", models.PositiveSmallIntegerField(verbose_name="semana ISO")),
                ("year", models.PositiveSmallIntegerField(verbose_name="año")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "created_by",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="teams_created",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="creado por",
                    ),
                ),
            ],
            options={
                "verbose_name": "equipo semanal",
                "verbose_name_plural": "equipos semanales",
                "ordering": ["-year", "-week_number", "project_name"],
            },
        ),
        migrations.CreateModel(
            name="WeeklyTeamMember",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("occupation", models.CharField(max_length=60, verbose_name="ocupación", help_text="Una palabra o frase corta que describe su foco esta semana.")),
                ("order", models.PositiveSmallIntegerField(default=0, verbose_name="orden")),
                (
                    "team",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="members",
                        to="teams.weeklyteam",
                        verbose_name="equipo",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="weekly_team_memberships",
                        to=settings.AUTH_USER_MODEL,
                        verbose_name="profesional",
                    ),
                ),
            ],
            options={
                "verbose_name": "integrante de equipo",
                "verbose_name_plural": "integrantes de equipo",
                "ordering": ["order", "user__first_name"],
            },
        ),
    ]
