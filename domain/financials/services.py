"""
Domain services for financial operations on projects.

Provides high-level methods for payment tracking, financial summaries,
and cash-flow chart data generation.
"""

from decimal import ROUND_HALF_UP, Decimal


class FinancialService:
    """Operations on project financial data (payments, cash flow, summaries)."""

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")

    @classmethod
    def get_project_financial_summary(cls, project_id: int) -> dict:
        """
        Build a comprehensive financial summary for a project.

        Returns:
            dict with keys:
                total_value, total_iva, total_executed, total_collected,
                pending_amount, collection_rate_pct, payments (list of dicts).
        """
        from apps.financials.models import PaymentMilestone
        from apps.projects.models import Project

        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            return {
                "total_value": 0,
                "total_iva": 0,
                "total_executed": 0,
                "total_collected": 0,
                "pending_amount": 0,
                "collection_rate_pct": 0,
                "payments": [],
            }

        payment_milestones = PaymentMilestone.objects.filter(
            project_id=project_id
        ).order_by("incidence_pct")

        total_value = cls.ZERO
        total_iva = cls.ZERO
        total_executed = cls.ZERO
        total_collected = cls.ZERO
        payments = []

        for pm in payment_milestones:
            proposed = Decimal(str(pm.proposed_value or 0))
            iva = Decimal(str(pm.iva_value or 0))
            executed = Decimal(str(pm.executed_value or 0))
            collected = Decimal(str(pm.collection_value or 0))

            total_value += proposed
            total_iva += iva
            total_executed += executed
            total_collected += collected

            payments.append(
                {
                    "id": pm.id,
                    "concept": pm.concept,
                    "proposed_value": float(proposed),
                    "iva_value": float(iva),
                    "total_with_iva": float(proposed + iva),
                    "incidence_pct": float(pm.incidence_pct or 0),
                    "status": pm.status,
                    "discount_pct": float(pm.discount_pct or 0),
                    "discount_value": float(pm.discount_value or 0),
                    "executed_value": float(executed),
                    "invoice_number": pm.invoice_number,
                    "invoice_value": float(pm.invoice_value or 0),
                    "billing_date": pm.billing_date,
                    "collection_value": float(collected),
                    "collection_date": pm.collection_date,
                    "difference": float(pm.difference or 0),
                    "notes": pm.notes,
                }
            )

        pending_amount = total_value - total_collected

        if total_value > cls.ZERO:
            collection_rate_pct = (
                total_collected / total_value * cls.HUNDRED
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            collection_rate_pct = cls.ZERO

        return {
            "total_value": float(total_value),
            "total_iva": float(total_iva),
            "total_executed": float(total_executed),
            "total_collected": float(total_collected),
            "pending_amount": float(pending_amount),
            "collection_rate_pct": float(collection_rate_pct),
            "payments": payments,
        }

    @staticmethod
    def update_payment_status(payment_id: int, status: str, **kwargs) -> None:
        """
        Update a payment milestone's status and recalculate its difference.

        Args:
            payment_id: Primary key of the PaymentMilestone.
            status:     New status string (one of PaymentMilestone.Status).
            **kwargs:   Additional fields to update (e.g. collection_value,
                        collection_date, invoice_number, executed_value).
        """
        from apps.financials.models import PaymentMilestone

        pm = PaymentMilestone.objects.get(pk=payment_id)
        pm.status = status

        # Apply any extra field updates
        updatable_fields = {
            "collection_value",
            "collection_date",
            "invoice_number",
            "invoice_value",
            "billing_date",
            "executed_value",
            "discount_pct",
            "discount_value",
            "notes",
        }

        for field, value in kwargs.items():
            if field in updatable_fields:
                setattr(pm, field, value)

        # The model's save() method recalculates difference automatically
        pm.save()

    @classmethod
    def get_cashflow_data(cls, project_id: int) -> dict:
        """
        Generate cash-flow chart data for ECharts visualisation.

        Returns:
            dict with keys:
                labels   -- list of payment concept strings
                proposed -- list of proposed values (floats)
                executed -- list of executed values (floats)
                collected -- list of collected values (floats)
        """
        from apps.financials.models import PaymentMilestone

        payment_milestones = PaymentMilestone.objects.filter(
            project_id=project_id
        ).order_by("incidence_pct")

        labels = []
        proposed = []
        executed = []
        collected = []

        for pm in payment_milestones:
            labels.append(pm.concept)
            proposed.append(float(pm.proposed_value or 0))
            executed.append(float(pm.executed_value or 0))
            collected.append(float(pm.collection_value or 0))

        return {
            "labels": labels,
            "proposed": proposed,
            "executed": executed,
            "collected": collected,
        }
