from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.views.generic import DetailView, FormView, TemplateView

from apps.imports.forms import ImportUploadForm
from apps.imports.models import ImportJob
from apps.imports.parsers import CORSheetParser, HolidaysCSVParser
from apps.imports.parsers_loggro import LoggroAccountingParser


# ---------------------------------------------------------------------------
# Import Wizard
# ---------------------------------------------------------------------------
class ImportWizardView(LoginRequiredMixin, TemplateView):
    """
    Landing page for the import module.  Shows available import types,
    instructions, and links to start an upload.
    """

    template_name = "imports/wizard.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["source_types"] = ImportJob.SourceType.choices
        context["recent_jobs"] = (
            ImportJob.objects.filter(uploaded_by=self.request.user)
            .order_by("-created_at")[:10]
        )
        return context


# ---------------------------------------------------------------------------
# Upload CSV
# ---------------------------------------------------------------------------
class UploadCSVView(LoginRequiredMixin, FormView):
    """
    Handles CSV file upload.  Stores the file via an ImportJob record
    and redirects to the preview page.
    """

    template_name = "imports/upload.html"
    form_class = ImportUploadForm

    def get_initial(self):
        initial = super().get_initial()
        source_type = self.request.GET.get("type")
        if source_type:
            initial["source_type"] = source_type
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        source_type = self.request.GET.get("type", "")
        type_labels = dict(ImportJob.SourceType.choices)
        if source_type in type_labels:
            context["selected_type_label"] = type_labels[source_type]
        return context

    def form_valid(self, form):
        uploaded_file = form.cleaned_data["file"]
        source_type = form.cleaned_data["source_type"]

        job = ImportJob.objects.create(
            uploaded_by=self.request.user,
            file=uploaded_file,
            source_type=source_type,
            status=ImportJob.Status.UPLOADED,
        )

        messages.success(
            self.request,
            f"Archivo subido correctamente. Trabajo de importación #{job.pk} creado.",
        )
        return redirect("imports:preview", pk=job.pk)

    def form_invalid(self, form):
        messages.error(self.request, "Por favor corrija los errores del formulario.")
        return super().form_invalid(form)


# ---------------------------------------------------------------------------
# Preview Import
# ---------------------------------------------------------------------------
class PreviewImportView(LoginRequiredMixin, DetailView):
    """
    Shows the parsed data from the uploaded file so the user can review
    it before confirming the import.
    """

    model = ImportJob
    template_name = "imports/preview.html"
    context_object_name = "job"

    def get_queryset(self):
        return ImportJob.objects.filter(uploaded_by=self.request.user)

    def get_template_names(self):
        if self.object.source_type == ImportJob.SourceType.LOGGRO_ACCOUNTING:
            return ["imports/preview_loggro.html"]
        if self.object.source_type == ImportJob.SourceType.HOLIDAYS:
            return ["imports/preview_holidays.html"]
        return [self.template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        job = self.object

        parsed_data = None
        parse_errors = []

        if job.source_type == ImportJob.SourceType.COR_SHEET:
            try:
                parser = CORSheetParser(job.file.path)
                parsed_data = parser.parse()
            except Exception as exc:
                parse_errors.append(str(exc))
        elif job.source_type == ImportJob.SourceType.LOGGRO_ACCOUNTING:
            try:
                parser = LoggroAccountingParser(job.file.path)
                parsed_data = parser.parse()
            except Exception as exc:
                parse_errors.append(str(exc))

            # Extra context for Loggro-specific template
            if parsed_data:
                context["accounts_count"] = len(parsed_data.get("accounts", {}))
                context["cost_centers_count"] = len(parsed_data.get("cost_centers", {}))
                context["errors_count"] = len(parsed_data.get("errors", []))
                context["sample_records"] = parsed_data.get("records", [])[:20]
        elif job.source_type == ImportJob.SourceType.FINANCIAL:
            parsed_data = {"info": "Vista previa de Control Financiero pendiente."}
        elif job.source_type == ImportJob.SourceType.HOLIDAYS:
            try:
                parser = HolidaysCSVParser(job.file.path)
                parsed_data = parser.parse()
                if parsed_data.get("errors"):
                    parse_errors.extend(parsed_data["errors"])
            except Exception as exc:
                parse_errors.append(str(exc))

        context["parsed_data"] = parsed_data
        context["parse_errors"] = parse_errors

        # Mark job as previewed
        if not parse_errors and job.status == ImportJob.Status.UPLOADED:
            job.status = ImportJob.Status.PREVIEWED
            job.save(update_fields=["status", "updated_at"])

        return context


# ---------------------------------------------------------------------------
# Confirm Import
# ---------------------------------------------------------------------------
class ConfirmImportView(LoginRequiredMixin, DetailView):
    """
    Executes the actual import after user confirmation.
    Processes the parsed data and creates/updates Django model instances.
    """

    model = ImportJob
    template_name = "imports/confirm.html"
    context_object_name = "job"

    def get_queryset(self):
        return ImportJob.objects.filter(uploaded_by=self.request.user)

    def post(self, request, *args, **kwargs):
        job = self.get_object()

        if job.status not in (
            ImportJob.Status.PREVIEWED,
            ImportJob.Status.CONFIRMED,
        ):
            messages.error(
                request,
                "Este trabajo no se puede confirmar en su estado actual.",
            )
            return redirect("imports:preview", pk=job.pk)

        job.status = ImportJob.Status.CONFIRMED
        job.save(update_fields=["status", "updated_at"])

        # Execute import
        errors = []
        records_imported = 0
        records_total = 0

        try:
            if job.source_type == ImportJob.SourceType.COR_SHEET:
                parser = CORSheetParser(job.file.path)
                parsed_data = parser.parse()
                records_total, records_imported, errors = self._import_cor_data(
                    parsed_data, job
                )
            elif job.source_type == ImportJob.SourceType.LOGGRO_ACCOUNTING:
                parser = LoggroAccountingParser(job.file.path)
                parsed_data = parser.parse()
                records_total, records_imported, errors = self._import_loggro_data(
                    parsed_data, job
                )
            elif job.source_type == ImportJob.SourceType.FINANCIAL:
                pass  # Placeholder for financial import
            elif job.source_type == ImportJob.SourceType.HOLIDAYS:
                parser = HolidaysCSVParser(job.file.path)
                parsed_data = parser.parse()
                records_total, records_imported, errors = self._import_holidays_data(
                    parsed_data
                )

            job.records_total = records_total
            job.records_imported = records_imported
            job.records_failed = records_total - records_imported
            job.errors = errors
            job.status = ImportJob.Status.COMPLETED
            job.completed_at = timezone.now()
            job.save()

            messages.success(
                request,
                f"Importación completada: {records_imported}/{records_total} "
                f"registros importados.",
            )
        except Exception as exc:
            job.status = ImportJob.Status.FAILED
            job.errors = [str(exc)]
            job.save()
            messages.error(request, f"Error durante la importación: {exc}")

        return redirect("imports:wizard")

    @staticmethod
    def _import_holidays_data(parsed_data):
        """
        Upsert ColombianHoliday records from parsed CSV data.
        Returns (records_total, records_imported, errors).
        """
        from apps.financials.models import ColombianHoliday

        holidays = parsed_data.get("holidays", [])
        parse_errors = parsed_data.get("errors", [])
        records_total = len(holidays)
        records_imported = 0
        errors = list(parse_errors)

        for h in holidays:
            try:
                ColombianHoliday.objects.update_or_create(
                    date=h["date"],
                    defaults={
                        "name": h["name"],
                        "holiday_type": h["holiday_type"],
                    },
                )
                records_imported += 1
            except Exception as exc:
                errors.append(f"Festivo {h.get('date', '?')}: {exc}")

        return records_total, records_imported, errors

    @staticmethod
    def _import_cor_data(parsed_data, job):
        """
        Process parsed C.O.R. data and create/update project records.
        Returns (records_total, records_imported, errors).
        """
        errors = []
        records_total = 0
        records_imported = 0

        if not parsed_data:
            return records_total, records_imported, ["No se encontraron datos."]

        # Import project info
        project_info = parsed_data.get("project_info", {})
        if project_info:
            records_total += 1
            try:
                from apps.projects.models import Project

                project, _created = Project.objects.update_or_create(
                    code=project_info.get("code", ""),
                    defaults={
                        "name": project_info.get("name", ""),
                        "location": project_info.get("location", ""),
                        "status": Project.Status.ACTIVE,
                    },
                )
                records_imported += 1
            except Exception as exc:
                errors.append(f"Error importando proyecto: {exc}")

        # Import phases and services
        phases = parsed_data.get("phases", [])
        for phase_data in phases:
            services = phase_data.get("services", [])
            for svc in services:
                records_total += 1
                try:
                    records_imported += 1
                except Exception as exc:
                    errors.append(
                        f"Error importando servicio {svc.get('code', '?')}: {exc}"
                    )

        return records_total, records_imported, errors

    @staticmethod
    def _import_loggro_data(parsed_data, job):
        """
        Process parsed Loggro accounting data.
        Auto-creates AccountingAccount and CostCenterMapping records,
        then creates AccountingTransaction records.
        Returns (records_total, records_imported, errors).
        """
        from apps.financials.models import (
            AccountingAccount,
            AccountingTransaction,
            CostCenterMapping,
        )

        errors = []
        records = parsed_data.get("records", [])
        records_total = len(records)
        records_imported = 0

        # Auto-create accounts
        for code, name in parsed_data.get("accounts", {}).items():
            if code:
                account_type = ""
                first_digit = code[0] if code else ""
                type_map = {
                    "1": "ASSET", "2": "LIABILITY", "3": "EQUITY",
                    "4": "REVENUE", "5": "EXPENSE", "6": "COST",
                    "7": "COST",
                }
                account_type = type_map.get(first_digit, "")
                AccountingAccount.objects.update_or_create(
                    account_code=code,
                    defaults={"name": name, "account_type": account_type},
                )

        # Auto-create cost centers
        for code, name in parsed_data.get("cost_centers", {}).items():
            if code:
                CostCenterMapping.objects.get_or_create(
                    cost_center_code=code,
                    defaults={"cost_center_name": name},
                )

        # Build lookups
        account_lookup = {a.account_code: a for a in AccountingAccount.objects.all()}
        cc_lookup = {c.cost_center_code: c for c in CostCenterMapping.objects.all()}

        # Create transactions in bulk
        txns_to_create = []
        for idx, record in enumerate(records):
            try:
                account = account_lookup.get(record["account_code"])
                if not account:
                    errors.append(f"Fila {idx + 1}: cuenta {record['account_code']} no encontrada.")
                    continue

                cost_center = cc_lookup.get(record.get("cost_center_code", ""))

                txns_to_create.append(AccountingTransaction(
                    import_job=job,
                    document_date=record["document_date"],
                    document_type=record.get("document_type", ""),
                    document_number=record.get("document_number", ""),
                    account=account,
                    cost_center=cost_center,
                    third_party_nit=record.get("third_party_nit", ""),
                    third_party_name=record.get("third_party_name", ""),
                    description=record.get("description", ""),
                    debit=record.get("debit", 0),
                    credit=record.get("credit", 0),
                    balance=record.get("balance", 0),
                    period=record.get("period", ""),
                ))
                records_imported += 1
            except Exception as exc:
                errors.append(f"Fila {idx + 1}: {exc}")

        if txns_to_create:
            AccountingTransaction.objects.bulk_create(txns_to_create, batch_size=500)

        return records_total, records_imported, errors
