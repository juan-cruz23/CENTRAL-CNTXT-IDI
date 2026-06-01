from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0007_add_sidebar_visibility_flags"),
    ]

    operations = [
        migrations.CreateModel(
            name="Badge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(max_length=120, verbose_name="nombre")),
                ("emoji", models.CharField(default="🏅", max_length=10, verbose_name="emoji")),
                ("color", models.CharField(default="#C8A87A", max_length=7, verbose_name="color (hex)")),
                ("description", models.TextField(blank=True, verbose_name="descripción")),
                ("is_active", models.BooleanField(default=True, verbose_name="activa")),
            ],
            options={
                "verbose_name": "medalla",
                "verbose_name_plural": "medallas",
                "ordering": ["name"],
            },
        ),
        migrations.CreateModel(
            name="UserBadge",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("granted_at", models.DateTimeField(auto_now_add=True, verbose_name="otorgada el")),
                ("note", models.TextField(blank=True, verbose_name="nota / motivo")),
                ("badge", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_badges", to="accounts.badge", verbose_name="medalla")),
                ("granted_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="badges_granted", to=settings.AUTH_USER_MODEL, verbose_name="otorgada por")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="user_badges", to=settings.AUTH_USER_MODEL, verbose_name="usuario")),
            ],
            options={
                "verbose_name": "medalla de usuario",
                "verbose_name_plural": "medallas de usuarios",
                "ordering": ["granted_at"],
                "unique_together": {("user", "badge")},
            },
        ),
    ]
