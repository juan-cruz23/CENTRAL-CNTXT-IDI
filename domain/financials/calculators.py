"""
Domain calculators for project profitability analysis.

Provides detailed profitability breakdowns at the project level and
per-phase level, computing margins from revenue and direct costs.
"""

from decimal import ROUND_HALF_UP, Decimal


class ProfitabilityCalculator:
    """
    Computes profitability metrics for a given project.

    Uses service instance data (revenue from total_value, direct costs
    from real_operative_cost, deductions) to compute gross profit,
    margins, and projections.
    """

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")

    def __init__(self, project):
        """
        Args:
            project: A Project model instance.  Related service_instances
                     and phase_instances should be accessible.
        """
        self.project = project

    def calculate(self) -> dict:
        """
        Calculate overall profitability for the project.

        Returns:
            dict with keys:
                total_revenue          -- sum of service instance total_value
                direct_costs           -- sum of real_operative_cost
                total_deductions       -- sum of deductions
                gross_profit           -- total_revenue - direct_costs - total_deductions
                gross_margin_pct       -- gross_profit / total_revenue * 100
                current_profitability  -- gross_profit based on actual progress
                projected_profitability -- projected gross_profit at completion
        """
        service_instances = self.project.service_instances.all()

        total_revenue = self.ZERO
        direct_costs = self.ZERO
        total_deductions = self.ZERO
        weighted_progress_revenue = self.ZERO

        for si in service_instances:
            si_value = Decimal(str(si.total_value or 0))
            si_cost = Decimal(str(si.real_operative_cost or 0))
            si_deductions = Decimal(str(si.deductions or 0))
            si_progress = Decimal(str(si.progress_pct or 0))

            total_revenue += si_value
            direct_costs += si_cost
            total_deductions += si_deductions
            weighted_progress_revenue += si_value * si_progress / self.HUNDRED

        gross_profit = total_revenue - direct_costs - total_deductions

        if total_revenue > self.ZERO:
            gross_margin_pct = (
                gross_profit / total_revenue * self.HUNDRED
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            gross_margin_pct = self.ZERO

        # Current profitability: profit earned so far based on actual progress
        current_profitability = weighted_progress_revenue - direct_costs

        # Projected profitability: if current margins hold through completion
        if weighted_progress_revenue > self.ZERO:
            cost_ratio = direct_costs / weighted_progress_revenue
            projected_total_costs = total_revenue * cost_ratio
            projected_profitability = (
                total_revenue - projected_total_costs - total_deductions
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            projected_profitability = gross_profit

        return {
            "total_revenue": float(
                total_revenue.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "direct_costs": float(
                direct_costs.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "total_deductions": float(
                total_deductions.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            ),
            "gross_profit": float(
                gross_profit.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            ),
            "gross_margin_pct": float(gross_margin_pct),
            "current_profitability": float(
                current_profitability.quantize(
                    Decimal("0.01"), rounding=ROUND_HALF_UP
                )
            ),
            "projected_profitability": float(projected_profitability),
        }

    def calculate_by_phase(self) -> list:
        """
        Calculate profitability broken down by project phase instance.

        Returns:
            list of dicts, each containing:
                phase_id, phase_name, total_revenue, direct_costs,
                total_deductions, gross_profit, gross_margin_pct
        """
        phase_instances = self.project.phase_instances.select_related(
            "phase"
        ).prefetch_related("service_instances")

        results = []

        for pi in phase_instances:
            phase_revenue = self.ZERO
            phase_costs = self.ZERO
            phase_deductions = self.ZERO

            for si in pi.service_instances.all():
                phase_revenue += Decimal(str(si.total_value or 0))
                phase_costs += Decimal(str(si.real_operative_cost or 0))
                phase_deductions += Decimal(str(si.deductions or 0))

            phase_profit = phase_revenue - phase_costs - phase_deductions

            if phase_revenue > self.ZERO:
                phase_margin_pct = (
                    phase_profit / phase_revenue * self.HUNDRED
                ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            else:
                phase_margin_pct = self.ZERO

            phase_name = str(pi.phase) if pi.phase_id else f"Fase {pi.order}"

            results.append(
                {
                    "phase_id": pi.id,
                    "phase_name": phase_name,
                    "total_revenue": float(
                        phase_revenue.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    ),
                    "direct_costs": float(
                        phase_costs.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    ),
                    "total_deductions": float(
                        phase_deductions.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    ),
                    "gross_profit": float(
                        phase_profit.quantize(
                            Decimal("0.01"), rounding=ROUND_HALF_UP
                        )
                    ),
                    "gross_margin_pct": float(phase_margin_pct),
                }
            )

        return results
