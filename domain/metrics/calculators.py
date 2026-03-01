"""
Domain-layer calculators for Earned Value Management (EVM) metrics
and S-Curve data generation.

These calculators are pure domain logic with minimal Django ORM coupling,
designed to be called from Celery tasks, management commands, or views.
"""

from datetime import date
from decimal import ROUND_HALF_UP, Decimal


class EVMCalculator:
    """
    Computes Earned Value Management metrics for a given project based
    on its ServiceInstance data.

    EVM Formulas:
        BAC = project.total_value
        PV  = SUM(si.total_value * si.expected_progress_pct / 100)
        EV  = SUM(si.total_value * si.progress_pct / 100)
        AC  = SUM(si.real_operative_cost)
        SPI = EV / PV  (if PV > 0, else 0)
        CPI = EV / AC  (if AC > 0, else 0)
        SV  = EV - PV
        CV  = EV - AC
        EAC = BAC / CPI  (if CPI > 0, else BAC)
        ETC = EAC - AC
        VAC = BAC - EAC
    """

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")

    def __init__(self, project):
        """
        Args:
            project: A Project model instance with related service_instances
                     and a total_value attribute.
        """
        self.project = project

    def calculate(self) -> dict:
        """
        Compute all EVM metrics from the project's ServiceInstance data.

        Returns:
            dict with keys: bac, planned_value, earned_value, actual_cost,
            spi, cpi, schedule_variance, cost_variance, eac, etc, vac,
            overall_progress_pct, expected_progress_pct, schedule_deviation_pct,
            total_revenue, total_costs, projected_margin_pct.
        """
        service_instances = self.project.service_instances.all()

        # ------------------------------------------------------------------
        # Core EVM values
        # ------------------------------------------------------------------
        bac = Decimal(str(self.project.total_value or 0))

        planned_value = self.ZERO
        earned_value = self.ZERO
        actual_cost = self.ZERO

        # Accumulators for weighted progress calculation
        weighted_progress_sum = self.ZERO
        weighted_expected_sum = self.ZERO
        total_service_value = self.ZERO

        for si in service_instances:
            si_value = Decimal(str(si.total_value or 0))
            si_progress = Decimal(str(si.progress_pct or 0))
            si_expected = Decimal(str(si.expected_progress_pct or 0))
            si_actual_cost = Decimal(str(si.real_operative_cost or 0))

            planned_value += si_value * si_expected / self.HUNDRED
            earned_value += si_value * si_progress / self.HUNDRED
            actual_cost += si_actual_cost

            weighted_progress_sum += si_value * si_progress
            weighted_expected_sum += si_value * si_expected
            total_service_value += si_value

        # ------------------------------------------------------------------
        # Performance Indices
        # ------------------------------------------------------------------
        spi = (earned_value / planned_value) if planned_value > 0 else self.ZERO
        cpi = (earned_value / actual_cost) if actual_cost > 0 else self.ZERO

        # ------------------------------------------------------------------
        # Variances
        # ------------------------------------------------------------------
        schedule_variance = earned_value - planned_value
        cost_variance = earned_value - actual_cost

        # ------------------------------------------------------------------
        # Forecasts
        # ------------------------------------------------------------------
        eac = (bac / cpi) if cpi > 0 else bac
        etc = eac - actual_cost
        vac = bac - eac

        # ------------------------------------------------------------------
        # Progress (weighted by service value)
        # ------------------------------------------------------------------
        if total_service_value > 0:
            overall_progress_pct = (
                weighted_progress_sum / total_service_value
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
            expected_progress_pct = (
                weighted_expected_sum / total_service_value
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            overall_progress_pct = self.ZERO
            expected_progress_pct = self.ZERO

        # Schedule deviation as percentage difference
        if expected_progress_pct > 0:
            schedule_deviation_pct = (
                (overall_progress_pct - expected_progress_pct)
                / expected_progress_pct
                * self.HUNDRED
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            schedule_deviation_pct = self.ZERO

        # ------------------------------------------------------------------
        # Financial summary
        # ------------------------------------------------------------------
        total_revenue = earned_value
        total_costs = actual_cost
        if total_revenue > 0:
            projected_margin_pct = (
                (total_revenue - total_costs) / total_revenue * self.HUNDRED
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            projected_margin_pct = self.ZERO

        # ------------------------------------------------------------------
        # Quantize final values
        # ------------------------------------------------------------------
        return {
            "bac": bac.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "planned_value": planned_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "earned_value": earned_value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "actual_cost": actual_cost.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "spi": spi.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            "cpi": cpi.quantize(Decimal("0.0001"), rounding=ROUND_HALF_UP),
            "schedule_variance": schedule_variance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "cost_variance": cost_variance.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "eac": eac.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "etc": etc.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "vac": vac.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "overall_progress_pct": overall_progress_pct,
            "expected_progress_pct": expected_progress_pct,
            "schedule_deviation_pct": schedule_deviation_pct,
            "total_revenue": total_revenue.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "total_costs": total_costs.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP),
            "projected_margin_pct": projected_margin_pct,
        }

    def create_snapshot(self, snapshot_date=None):
        """
        Calculate EVM metrics and persist a new ProjectMetricSnapshot.

        Uses update_or_create to allow re-running on the same date
        (updates existing snapshot rather than raising IntegrityError).

        Args:
            snapshot_date: The date for the snapshot. Defaults to today.

        Returns:
            ProjectMetricSnapshot instance (created or updated).
        """
        from apps.metrics.models import ProjectMetricSnapshot

        if snapshot_date is None:
            snapshot_date = date.today()

        metrics = self.calculate()

        snapshot, _created = ProjectMetricSnapshot.objects.update_or_create(
            project=self.project,
            snapshot_date=snapshot_date,
            defaults=metrics,
        )
        return snapshot


class SCurveGenerator:
    """
    Generates S-Curve data series for ECharts visualization.

    Returns time-series arrays of Planned Value (PV), Earned Value (EV),
    and Actual Cost (AC) from historical metric snapshots.
    """

    def __init__(self, project):
        """
        Args:
            project: A Project model instance.
        """
        self.project = project

    def generate(self, start_date=None, end_date=None) -> dict:
        """
        Generate S-Curve data from historical snapshots.

        Args:
            start_date: Optional start date filter (str 'YYYY-MM-DD' or date).
            end_date: Optional end date filter (str 'YYYY-MM-DD' or date).

        Returns:
            dict with keys:
                - dates: list of date strings (ISO format)
                - planned_value: list of float values
                - earned_value: list of float values
                - actual_cost: list of float values
        """
        from apps.metrics.models import ProjectMetricSnapshot

        queryset = ProjectMetricSnapshot.objects.filter(
            project=self.project
        ).order_by("snapshot_date")

        if start_date:
            queryset = queryset.filter(snapshot_date__gte=start_date)
        if end_date:
            queryset = queryset.filter(snapshot_date__lte=end_date)

        snapshots = queryset.values_list(
            "snapshot_date",
            "planned_value",
            "earned_value",
            "actual_cost",
        )

        if snapshots:
            dates = []
            planned_values = []
            earned_values = []
            actual_costs = []

            for snap_date, pv, ev, ac in snapshots:
                dates.append(snap_date.isoformat())
                planned_values.append(float(pv))
                earned_values.append(float(ev))
                actual_costs.append(float(ac))

            return {
                "dates": dates,
                "planned_value": planned_values,
                "earned_value": earned_values,
                "actual_cost": actual_costs,
            }

        # ------------------------------------------------------------------
        # Fallback: generate projected S-Curve from service instance dates
        # when no snapshots exist yet.
        # ------------------------------------------------------------------
        return self._generate_from_service_instances()

    def _generate_from_service_instances(self) -> dict:
        """
        Build a projected S-Curve from ServiceInstance scheduled dates
        when no historical snapshots are available.

        Uses each service instance's planned start/end dates and total_value
        to create a cumulative planned value curve.
        """
        service_instances = self.project.service_instances.all().order_by(
            "projected_start_date"
        )

        if not service_instances.exists():
            return {
                "dates": [],
                "planned_value": [],
                "earned_value": [],
                "actual_cost": [],
            }

        # Collect date-value pairs for building the curve
        date_pv_map = {}

        for si in service_instances:
            si_start = getattr(si, "projected_start_date", None)
            si_end = getattr(si, "projected_end_date", None)
            si_value = float(si.total_value or 0)

            if not si_start or not si_end or si_value == 0:
                continue

            # Distribute value linearly across the service instance duration
            duration_days = (si_end - si_start).days
            if duration_days <= 0:
                # Point assignment on end date
                date_pv_map[si_end.isoformat()] = (
                    date_pv_map.get(si_end.isoformat(), 0) + si_value
                )
                continue

            daily_value = si_value / duration_days
            current = si_start
            from datetime import timedelta

            while current <= si_end:
                key = current.isoformat()
                date_pv_map[key] = date_pv_map.get(key, 0) + daily_value
                current += timedelta(days=1)

        if not date_pv_map:
            return {
                "dates": [],
                "planned_value": [],
                "earned_value": [],
                "actual_cost": [],
            }

        # Sort by date and build cumulative curve
        sorted_dates = sorted(date_pv_map.keys())
        cumulative = 0.0
        dates = []
        planned_values = []

        for d in sorted_dates:
            cumulative += date_pv_map[d]
            dates.append(d)
            planned_values.append(round(cumulative, 2))

        return {
            "dates": dates,
            "planned_value": planned_values,
            "earned_value": [0.0] * len(dates),
            "actual_cost": [0.0] * len(dates),
        }
