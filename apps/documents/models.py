from django.db import models

from apps.common.models import TimeStampedModel


class ProjectDocument(TimeStampedModel):
    """Documentos asociados a un proyecto o instancia de servicio."""

    class DocumentType(models.TextChoices):
        QUOTATION = "QUOTATION", "Cotización"
        CONTRACT = "CONTRACT", "Contrato"
        DELIVERABLE = "DELIVERABLE", "Entregable"
        SUPPORT = "SUPPORT", "Soporte"
        INVOICE = "INVOICE", "Factura"
        OTHER = "OTHER", "Otro"

    project = models.ForeignKey(
        "projects.Project",
        on_delete=models.CASCADE,
        related_name="documents",
        verbose_name="proyecto",
    )
    service_instance = models.ForeignKey(
        "projects.ServiceInstance",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="documents",
        verbose_name="instancia de servicio",
    )
    document_type = models.CharField(
        max_length=50,
        choices=DocumentType.choices,
        default=DocumentType.DELIVERABLE,
        verbose_name="tipo de documento",
    )
    name = models.CharField(
        max_length=300,
        verbose_name="nombre",
    )
    access_link = models.URLField(
        blank=True,
        verbose_name="enlace de acceso",
        help_text="Enlace a Google Drive u otro servicio de almacenamiento.",
    )
    file = models.FileField(
        upload_to="documents/%Y/%m/",
        blank=True,
        verbose_name="archivo",
    )
    delivery_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de entrega",
    )
    approval_date = models.DateField(
        null=True,
        blank=True,
        verbose_name="fecha de aprobacion",
    )
    uploaded_by = models.ForeignKey(
        "accounts.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="uploaded_documents",
        editable=False,
        verbose_name="subido por",
    )
    notes = models.TextField(
        blank=True,
        verbose_name="notas",
    )

    class Meta:
        verbose_name = "documento de proyecto"
        verbose_name_plural = "documentos de proyecto"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.project} - {self.name}"
