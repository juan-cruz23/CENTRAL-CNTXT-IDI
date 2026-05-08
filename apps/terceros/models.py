from django.db import models

from apps.common.models import TimeStampedModel


class ThirdParty(TimeStampedModel):
    """Unified third-party entity supporting multiple relationship types."""

    class RelationshipType(models.TextChoices):
        CLIENTE = "CLIENTE", "Cliente"
        PROSPECTO = "PROSPECTO", "Prospecto"
        GROWTH_PARTNER = "GROWTH_PARTNER", "Growth Partner"
        EMBAJADOR = "EMBAJADOR", "Embajador"
        PROVEEDOR = "PROVEEDOR", "Proveedor"
        EQUIPO_INTERNO = "EQUIPO_INTERNO", "Equipo Interno"
        ALIADO_ESTRATEGICO = "ALIADO_ESTRATEGICO", "Aliado Estratégico"
        OTRO = "OTRO", "Otro"

    class ClientCategory(models.TextChoices):
        BLACK = "BLACK", "Black"
        GOLD = "GOLD", "Gold"
        SILVER = "SILVER", "Silver"
        SELECT = "SELECT", "Select"

    class DocumentType(models.TextChoices):
        NIT = "NIT", "NIT"
        CC = "CC", "Cédula de ciudadanía"
        CE = "CE", "Cédula de extranjería"
        PASAPORTE = "PASAPORTE", "Pasaporte"
        OTRO = "OTRO", "Otro"

    class PersonType(models.TextChoices):
        NATURAL = "NATURAL", "Persona Natural"
        JURIDICA = "JURIDICA", "Persona Jurídica"

    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )
    person_type = models.CharField(
        max_length=10,
        choices=PersonType.choices,
        default=PersonType.NATURAL,
        verbose_name="tipo de persona",
    )
    company = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="empresa",
    )
    document_type = models.CharField(
        max_length=15,
        choices=DocumentType.choices,
        default=DocumentType.NIT,
        blank=True,
        verbose_name="tipo de documento",
    )
    nit = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="número de documento",
        help_text="Número de documento (NIT, cédula, etc.) para cruce con Loggro.",
    )
    relationship_type = models.CharField(
        max_length=30,
        choices=RelationshipType.choices,
        verbose_name="tipo de relación",
    )
    client_category = models.CharField(
        max_length=10,
        choices=ClientCategory.choices,
        blank=True,
        verbose_name="categoría de cliente",
        help_text="Solo aplica cuando el tipo de relación es Cliente.",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="correo electrónico",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="teléfono",
    )
    city = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="ciudad",
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name="activo",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )
    legacy_client_id = models.IntegerField(
        null=True,
        blank=True,
        editable=False,
        verbose_name="ID de cliente legacy",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "tercero"
        verbose_name_plural = "terceros"

    def __str__(self):
        return self.name


class ThirdPartyContact(TimeStampedModel):
    """Contact person associated with a third party."""

    third_party = models.ForeignKey(
        ThirdParty,
        on_delete=models.CASCADE,
        related_name="contacts",
        verbose_name="tercero",
    )
    name = models.CharField(
        max_length=200,
        verbose_name="nombre",
    )
    role = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="cargo",
    )
    email = models.EmailField(
        blank=True,
        verbose_name="correo electrónico",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name="teléfono",
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name="contacto principal",
    )

    class Meta:
        ordering = ["-is_primary", "name"]
        verbose_name = "contacto de tercero"
        verbose_name_plural = "contactos de tercero"

    def __str__(self):
        return f"{self.name} ({self.third_party})"
