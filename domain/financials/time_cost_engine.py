"""
Time-based Cost Allocation Engine.

Calculates real project costs from WeeklyTimeDistribution data.

Logic:
  For each user who submitted a distribution for a week:
    weekly_cost = (hourly_rate + hourly_overhead) × weekly_available_hours
    For each project entry:
      project_cost += weekly_cost × (percentage / 100)

  Then aggregates by month into CostAllocation records.
"""

from collections import defaultdict
from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

ZERO = Decimal("0")
WEEKLY_HOURS_DEFAULT = 40


def get_user_weekly_cost(user):
    """Calculate the full weekly cost of a user."""
    from apps.capacity.models import TeamMemberCapacity
    from django.db.models import Q

    today = date.today()
    cap = TeamMemberCapacity.objects.filter(
        user=user,
        effective_from__lte=today,
    ).filter(
        Q(effective_until__isnull=True) | Q(effective_until__gte=today),
    ).first()

    weekly_hours = Decimal(str(cap.weekly_available_hours)) if cap else Decimal(str(WEEKLY_HOURS_DEFAULT))
    rate = user.hourly_rate or ZERO
    overhead = user.hourly_overhead or ZERO
    return (rate + overhead) * weekly_hours


def calculate_week_costs(week_start):
    """
    Calculate project costs for a specific week based on all submitted distributions.

    Returns:
        dict: {project_id: {
            'amount': Decimal,
            'details': [{'user': str, 'pct': int, 'cost': Decimal}, ...],
        }}
    """
    from apps.timetracking.models import WeeklyTimeDistribution

    distributions = WeeklyTimeDistribution.objects.filter(
        week_start=week_start,
        status=WeeklyTimeDistribution.Status.SUBMITTED,
    ).prefetch_related("entries__project").select_related("user")

    project_costs = defaultdict(lambda: {"amount": ZERO, "details": []})

    for dist in distributions:
        weekly_cost = get_user_weekly_cost(dist.user)

        for entry in dist.entries.all():
            pct = Decimal(str(entry.percentage))
            cost = (weekly_cost * pct / Decimal("100")).quantize(
                Decimal("0.01"), rounding=ROUND_HALF_UP
            )
            project_costs[entry.project_id]["amount"] += cost
            project_costs[entry.project_id]["details"].append({
                "user": dist.user.get_full_name(),
                "user_id": dist.user_id,
                "pct": entry.percentage,
                "cost": cost,
                "weekly_cost": weekly_cost,
            })

    return dict(project_costs)


def calculate_month_costs(year, month):
    """
    Aggregate weekly costs for an entire month.

    Returns:
        dict: {project_id: {
            'amount': Decimal,
            'weeks': int,
            'detail_by_user': {user_id: {'name': str, 'total_cost': Decimal, 'weeks': int}},
        }}
    """
    # Find all Mondays in the given month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)

    # Get the Monday of the first week that overlaps with this month
    start_monday = first_day - timedelta(days=first_day.weekday())
    # Get the Monday of the last week that overlaps
    end_monday = last_day - timedelta(days=last_day.weekday())

    project_totals = defaultdict(lambda: {
        "amount": ZERO,
        "weeks": 0,
        "detail_by_user": defaultdict(lambda: {"name": "", "total_cost": ZERO, "weeks": 0}),
    })

    current = start_monday
    while current <= end_monday:
        week_costs = calculate_week_costs(current)
        for project_id, data in week_costs.items():
            project_totals[project_id]["amount"] += data["amount"]
            project_totals[project_id]["weeks"] += 1
            for detail in data["details"]:
                uid = detail["user_id"]
                project_totals[project_id]["detail_by_user"][uid]["name"] = detail["user"]
                project_totals[project_id]["detail_by_user"][uid]["total_cost"] += detail["cost"]
                project_totals[project_id]["detail_by_user"][uid]["weeks"] += 1
        current += timedelta(weeks=1)

    return dict(project_totals)


def save_month_allocations(year, month, dry_run=False):
    """
    Calculate and save CostAllocation records for a month.

    Returns summary dict.
    """
    from apps.financials.models import CostAllocation, CostAllocationPeriod
    from apps.projects.models import Project

    period_str = f"{year}-{month:02d}"
    month_costs = calculate_month_costs(year, month)

    if not month_costs:
        return {
            "period": period_str,
            "projects": [],
            "total_cost": ZERO,
            "saved": False,
            "message": "No hay distribuciones de tiempo enviadas para este periodo.",
        }

    total_cost = sum(d["amount"] for d in month_costs.values())

    projects_summary = []
    for project_id, data in month_costs.items():
        try:
            project = Project.objects.get(pk=project_id)
        except Project.DoesNotExist:
            continue

        pct = (data["amount"] / total_cost * Decimal("100")).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        ) if total_cost > 0 else ZERO

        users_detail = [
            {"name": u["name"], "cost": u["total_cost"], "weeks": u["weeks"]}
            for u in data["detail_by_user"].values()
        ]

        projects_summary.append({
            "project_code": project.code,
            "project_name": project.name,
            "project_id": project.pk,
            "amount": data["amount"],
            "pct": pct,
            "weeks": data["weeks"],
            "users": users_detail,
        })

    projects_summary.sort(key=lambda x: x["amount"], reverse=True)

    if not dry_run:
        # Create or update period
        first_day = date(year, month, 1)
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)

        period_obj, _ = CostAllocationPeriod.objects.update_or_create(
            period=period_str,
            defaults={
                "start_date": first_day,
                "end_date": last_day,
                "total_costs": total_cost,
            },
        )

        # Delete old allocations for this period (recalculate)
        CostAllocation.objects.filter(period=period_obj, cost_type="OPERATIVE").delete()

        for ps in projects_summary:
            CostAllocation.objects.create(
                period=period_obj,
                project_id=ps["project_id"],
                cost_type="OPERATIVE",
                allocated_amount=ps["amount"],
                allocation_pct=ps["pct"],
                source_description=f"Distribución de tiempo - {ps['weeks']} semanas",
            )

    return {
        "period": period_str,
        "projects": projects_summary,
        "total_cost": total_cost,
        "saved": not dry_run,
    }


def get_project_profitability(project_id):
    """
    Calculate real profitability for a project using time distributions.

    Returns:
        dict with fee, cost, margin data.
    """
    from apps.financials.models import CostAllocation, PaymentMilestone
    from apps.projects.models import Project
    from django.db.models import Sum

    project = Project.objects.get(pk=project_id)

    # Revenue: total collected from payment milestones
    payment_data = PaymentMilestone.objects.filter(
        project=project,
    ).aggregate(
        total_invoiced=Sum("executed_value"),
        total_collected=Sum("collection_value"),
    )
    total_invoiced = payment_data["total_invoiced"] or ZERO
    total_collected = payment_data["total_collected"] or ZERO

    # Cost: sum of all OPERATIVE cost allocations
    total_cost = CostAllocation.objects.filter(
        project=project,
        cost_type="OPERATIVE",
    ).aggregate(total=Sum("allocated_amount"))["total"] or ZERO

    # Margins
    fee = project.total_value or ZERO
    utility = fee - total_cost
    margin_pct = (utility / fee * Decimal("100")).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    ) if fee > 0 else ZERO

    return {
        "project": project,
        "fee": fee,
        "total_invoiced": total_invoiced,
        "total_collected": total_collected,
        "total_cost": total_cost,
        "utility": utility,
        "margin_pct": margin_pct,
    }
