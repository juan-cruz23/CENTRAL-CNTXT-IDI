"""
Cost Allocation Engine - distributes monthly costs proportionally
among active projects based on estimated hours (prorrateo).
"""

from decimal import ROUND_HALF_UP, Decimal


class CostAllocationEngine:
    """
    Allocates costs from accounting transactions to projects
    proportionally based on projected hours from ServiceInstances.
    """

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")

    def allocate_period(self, period_str: str, dry_run: bool = False) -> dict:
        """
        Execute cost allocation for a given period.

        Steps:
        1. Sum cost/expense transactions for the period (accounts 5xxxx, 6xxxx, 7xxxx)
        2. Get active projects with their total projected hours
        3. Calculate proportion: project_hours / total_hours
        4. Create CostAllocation records per project
        5. Update ServiceInstance.real_operative_cost

        Args:
            period_str: Period in "YYYY-MM" format.
            dry_run: If True, return preview without creating records.

        Returns:
            dict with allocation summary.
        """
        from apps.financials.models import (
            CostAllocation,
            CostAllocationPeriod,
        )

        total_costs = self._get_period_costs(period_str)
        project_weights = self._get_project_weights()

        if not project_weights:
            return {
                "period": period_str,
                "total_costs": float(total_costs),
                "projects": [],
                "message": "No hay proyectos activos con horas estimadas.",
            }

        total_hours = sum(w["hours"] for w in project_weights)
        if total_hours <= self.ZERO:
            return {
                "period": period_str,
                "total_costs": float(total_costs),
                "projects": [],
                "message": "No hay horas estimadas en los proyectos activos.",
            }

        allocations = []
        for pw in project_weights:
            pct = (pw["hours"] / total_hours * self.HUNDRED).quantize(
                Decimal("0.0001"), rounding=ROUND_HALF_UP
            )
            amount = (total_costs * pw["hours"] / total_hours).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            allocations.append({
                "project_id": pw["project_id"],
                "project_code": pw["project_code"],
                "project_name": pw["project_name"],
                "hours": float(pw["hours"]),
                "pct": float(pct),
                "amount": float(amount),
            })

        result = {
            "period": period_str,
            "total_costs": float(total_costs),
            "total_hours": float(total_hours),
            "projects": allocations,
        }

        if not dry_run:
            # Parse period dates
            import calendar
            from datetime import date

            year, month = int(period_str[:4]), int(period_str[5:7])
            last_day = calendar.monthrange(year, month)[1]
            start_date = date(year, month, 1)
            end_date = date(year, month, last_day)

            period_obj, _ = CostAllocationPeriod.objects.update_or_create(
                period=period_str,
                defaults={
                    "start_date": start_date,
                    "end_date": end_date,
                    "total_costs": total_costs,
                },
            )

            # Clear existing allocations for this period
            period_obj.allocations.all().delete()

            for alloc in allocations:
                CostAllocation.objects.create(
                    period=period_obj,
                    project_id=alloc["project_id"],
                    cost_type=CostAllocation.CostType.OPERATIVE,
                    allocated_amount=Decimal(str(alloc["amount"])),
                    allocation_pct=Decimal(str(alloc["pct"])),
                    source_description=f"Prorrateo automático {period_str}",
                )

            # Update ServiceInstance.real_operative_cost
            self._update_service_costs(allocations)

            result["saved"] = True

        return result

    def _get_period_costs(self, period_str: str) -> Decimal:
        """Sum cost/expense transactions for the period."""
        from apps.financials.models import AccountingTransaction

        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        # Accounts starting with 5 (expenses), 6 (costs), 7 (costs)
        result = AccountingTransaction.objects.filter(
            period=period_str,
            account__account_code__regex=r'^[567]',
        ).aggregate(
            total_debit=Coalesce(Sum("debit"), self.ZERO),
            total_credit=Coalesce(Sum("credit"), self.ZERO),
        )

        # Net cost = debits - credits for expense/cost accounts
        return result["total_debit"] - result["total_credit"]

    def _get_project_weights(self) -> list:
        """
        Get weight for each active project.
        Weight = SUM(projected_hours) from its ServiceInstances.
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        from apps.projects.models import Project

        projects = Project.objects.filter(
            status=Project.Status.ACTIVE,
        ).annotate(
            total_hours=Coalesce(Sum("service_instances__projected_hours"), self.ZERO),
        ).filter(total_hours__gt=0)

        return [
            {
                "project_id": p.pk,
                "project_code": p.code,
                "project_name": p.name,
                "hours": Decimal(str(p.total_hours)),
            }
            for p in projects
        ]

    @staticmethod
    def _update_service_costs(allocations):
        """
        Distribute allocated costs to individual ServiceInstances
        within each project, proportionally by projected_hours.
        """
        from apps.projects.models import ServiceInstance

        for alloc in allocations:
            services = ServiceInstance.objects.filter(
                project_id=alloc["project_id"],
                projected_hours__gt=0,
            )
            total_hours = sum(float(s.projected_hours) for s in services)
            if total_hours <= 0:
                continue

            for si in services:
                si_pct = float(si.projected_hours) / total_hours
                si.real_operative_cost = Decimal(str(alloc["amount"] * si_pct)).quantize(
                    Decimal("0.01")
                )
                si.save(update_fields=["real_operative_cost", "updated_at"])
