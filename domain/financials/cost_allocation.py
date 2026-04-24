"""
Cost Allocation Engine - distributes monthly costs proportionally
among active projects based on operative-line weights + estimated hours.

Two-level distribution:
  1. Total cost → split by operative line (weight_pct defined per quarter)
  2. Each line's share → split by project hours within that line
"""

import calendar
from datetime import date
from decimal import ROUND_HALF_UP, Decimal


def _period_to_quarter(period_str: str) -> str:
    """Return "YYYY-QN" for a "YYYY-MM" period string."""
    month = int(period_str[5:7])
    quarter = (month - 1) // 3 + 1
    return f"{period_str[:4]}-Q{quarter}"


class CostAllocationEngine:
    ZERO = Decimal("0")
    HUNDRED = Decimal("100")

    def allocate_period(self, period_str: str, dry_run: bool = False) -> dict:
        """
        Execute cost allocation for a given period.

        Steps:
        1. Sum cost/expense transactions for the period (accounts 5xxxx, 6xxxx, 7xxxx)
        2. Resolve operative-line weights for the quarter (manual or auto-proposed)
        3. For each line: split line's share among its projects by projected hours
        4. Persist CostAllocationPeriod + CostAllocation records + ServiceInstance costs

        Args:
            period_str: Period in "YYYY-MM" format.
            dry_run: If True, return preview without creating records.
        """
        total_costs = self._get_period_costs(period_str)
        quarter = _period_to_quarter(period_str)

        projects_by_line = self._get_projects_by_line()
        if not projects_by_line:
            return {
                "period": period_str,
                "quarter": quarter,
                "total_costs": float(total_costs),
                "by_line": [],
                "projects": [],
                "message": "No hay proyectos activos con horas estimadas.",
            }

        line_weights, weight_source = self._resolve_line_weights(quarter, projects_by_line)

        total_hours_all = sum(
            pw["hours"]
            for line_data in projects_by_line.values()
            for pw in line_data
        )

        by_line = []
        all_projects = []

        for line_code, line_weight in line_weights.items():
            line_projects = projects_by_line.get(line_code, [])
            if not line_projects:
                continue

            line_amount = (total_costs * line_weight / self.HUNDRED).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            line_hours = sum(pw["hours"] for pw in line_projects)

            project_allocs = []
            for pw in line_projects:
                within_line_pct = (
                    (pw["hours"] / line_hours * self.HUNDRED).quantize(
                        Decimal("0.0001"), rounding=ROUND_HALF_UP
                    )
                    if line_hours > self.ZERO else self.ZERO
                )
                global_pct = (
                    (pw["hours"] / total_hours_all * self.HUNDRED).quantize(
                        Decimal("0.0001"), rounding=ROUND_HALF_UP
                    )
                    if total_hours_all > self.ZERO else self.ZERO
                )
                amount = (
                    (line_amount * pw["hours"] / line_hours).quantize(
                        Decimal("0.01"), rounding=ROUND_HALF_UP
                    )
                    if line_hours > self.ZERO else self.ZERO
                )

                entry = {
                    "project_id": pw["project_id"],
                    "project_code": pw["project_code"],
                    "project_name": pw["project_name"],
                    "line_code": line_code,
                    "line_name": pw["line_name"],
                    "hours": float(pw["hours"]),
                    "within_line_pct": float(within_line_pct),
                    "pct": float(global_pct),
                    "amount": float(amount),
                }
                project_allocs.append(entry)
                all_projects.append(entry)

            by_line.append({
                "line_code": line_code,
                "line_name": line_projects[0]["line_name"] if line_projects else line_code,
                "weight_pct": float(line_weight),
                "line_amount": float(line_amount),
                "line_hours": float(line_hours),
                "projects": project_allocs,
            })

        result = {
            "period": period_str,
            "quarter": quarter,
            "total_costs": float(total_costs),
            "total_hours": float(total_hours_all),
            "weight_source": weight_source,
            "by_line": by_line,
            "projects": all_projects,
        }

        if not dry_run:
            self._persist(period_str, total_costs, all_projects)
            result["saved"] = True

        return result

    def propose_line_weights(self, quarter: str) -> list:
        """
        Return auto-proposed weights based on projected hours per operative line.
        Used to pre-fill the configuration form.
        """
        projects_by_line = self._get_projects_by_line()
        if not projects_by_line:
            return []

        total_hours = sum(
            pw["hours"]
            for line_data in projects_by_line.values()
            for pw in line_data
        )
        if total_hours <= self.ZERO:
            return []

        proposals = []
        for line_code, projects in projects_by_line.items():
            line_hours = sum(pw["hours"] for pw in projects)
            pct = (line_hours / total_hours * self.HUNDRED).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            proposals.append({
                "line_code": line_code,
                "line_name": projects[0]["line_name"],
                "line_id": projects[0]["line_id"],
                "proposed_pct": float(pct),
                "hours": float(line_hours),
            })
        return proposals

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _resolve_line_weights(self, quarter: str, projects_by_line: dict) -> tuple:
        """
        Return (weights_dict, source) where weights_dict maps line_code → Decimal pct.
        Source is "manual" if saved weights exist, "auto" if computed from hours.
        """
        from apps.financials.models import LineAllocationWeight

        saved = LineAllocationWeight.objects.filter(quarter=quarter).select_related(
            "business_unit"
        )
        if saved.exists():
            return (
                {w.business_unit.code: w.weight_pct for w in saved},
                "manual",
            )

        total_hours = sum(
            pw["hours"]
            for line_data in projects_by_line.values()
            for pw in line_data
        )
        weights = {}
        for line_code, projects in projects_by_line.items():
            line_hours = sum(pw["hours"] for pw in projects)
            weights[line_code] = (
                (line_hours / total_hours * self.HUNDRED).quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
                if total_hours > self.ZERO
                else self.ZERO
            )
        return weights, "auto"

    def _get_period_costs(self, period_str: str) -> Decimal:
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        from apps.financials.models import AccountingTransaction

        result = AccountingTransaction.objects.filter(
            period=period_str,
            account__account_code__regex=r"^[567]",
        ).aggregate(
            total_debit=Coalesce(Sum("debit"), self.ZERO),
            total_credit=Coalesce(Sum("credit"), self.ZERO),
        )
        return result["total_debit"] - result["total_credit"]

    def _get_projects_by_line(self) -> dict:
        """
        Return dict mapping BusinessUnit.code (MADE/SELECT) → list of project weight dicts.
        Only includes active projects with projected hours and a business unit assigned.
        """
        from django.db.models import Sum
        from django.db.models.functions import Coalesce

        from apps.projects.models import Project

        projects = (
            Project.objects.filter(status=Project.Status.ACTIVE)
            .select_related("business_unit")
            .annotate(
                total_hours=Coalesce(
                    Sum("service_instances__projected_hours"), self.ZERO
                )
            )
            .filter(total_hours__gt=0, business_unit__isnull=False)
        )

        by_line: dict = {}
        for p in projects:
            code = p.business_unit.code
            by_line.setdefault(code, [])
            by_line[code].append({
                "project_id": p.pk,
                "project_code": p.code,
                "project_name": p.name,
                "line_id": p.business_unit.pk,
                "line_code": code,
                "line_name": p.business_unit.name,
                "hours": Decimal(str(p.total_hours)),
            })
        return by_line

    def _persist(self, period_str, total_costs, all_projects):
        from apps.financials.models import CostAllocation, CostAllocationPeriod

        year, month = int(period_str[:4]), int(period_str[5:7])
        last_day = calendar.monthrange(year, month)[1]

        period_obj, _ = CostAllocationPeriod.objects.update_or_create(
            period=period_str,
            defaults={
                "start_date": date(year, month, 1),
                "end_date": date(year, month, last_day),
                "total_costs": total_costs,
            },
        )
        period_obj.allocations.all().delete()

        for alloc in all_projects:
            CostAllocation.objects.create(
                period=period_obj,
                project_id=alloc["project_id"],
                cost_type=CostAllocation.CostType.OPERATIVE,
                allocated_amount=Decimal(str(alloc["amount"])),
                allocation_pct=Decimal(str(alloc["pct"])),
                source_description=(
                    f"Prorrateo {period_str} — "
                    f"línea {alloc['line_code']} {alloc['within_line_pct']:.2f}% interno"
                ),
            )

        self._update_service_costs(all_projects)

    @staticmethod
    def _update_service_costs(allocations):
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
                si.real_operative_cost = Decimal(
                    str(alloc["amount"] * si_pct)
                ).quantize(Decimal("0.01"))
                si.save(update_fields=["real_operative_cost", "updated_at"])
