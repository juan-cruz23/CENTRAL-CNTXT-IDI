from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=100, unique=True, verbose_name="nombre")),
                ("iso_code", models.CharField(max_length=3, unique=True, verbose_name="código ISO")),
                ("is_active", models.BooleanField(default=True, verbose_name="activo")),
            ],
            options={"verbose_name": "país", "verbose_name_plural": "países", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="Municipality",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=150, verbose_name="nombre")),
                ("department", models.CharField(max_length=100, verbose_name="departamento")),
                ("is_active", models.BooleanField(default=True, verbose_name="activo")),
                ("country", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="municipalities", to="geography.country", verbose_name="país")),
            ],
            options={"verbose_name": "municipio", "verbose_name_plural": "municipios", "ordering": ["department", "name"]},
        ),
        migrations.AlterUniqueTogether(
            name="municipality",
            unique_together={("name", "department", "country")},
        ),
    ]
