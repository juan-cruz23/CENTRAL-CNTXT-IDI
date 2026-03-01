"""
Domain services for team capacity management.

Provides allocation tracking, overload/underload detection, capacity
alerts, and simulation utilities for workforce planning.
"""

from datetime import date, timedelta
from decimal import ROUND_HALF_UP, Decimal

from django.db import transaction
from django.db.models import Q, Sum


class CapacityService:
    """Operations for querying and analysing team member capacity."""

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")
    DEFAULT_WEEKLY_HOURS = Decimal("40")

    @classmethod
    def get_user_capacity(cls, user_id: int, week_start: date) -> dict:
        """
        Calculate capacity data for a single user for a given week.

        Args:
            user_id:    Primary key of the User.
            week_start: Monday of the target week.

        Returns:
            dict with keys:
                available_hours   -- weekly hours available
                allocated_hours   -- total hours allocated across projects
                allocation_pct    -- allocated / available * 100
                projects          -- list of {project_code, project_name,
                                     weekly_hours, role} dicts
        """
        from apps.capacity.models import ProjectAllocation, TeamMemberCapacity

        # Determine available hours for this week
        capacity = (
            TeamMemberCapacity.objects.filter(
                user_id=user_id,
                effective_from__lte=week_start,
            )
            .filter(
                Q(effective_until__isnull=True)
                | Q(effective_until__gte=week_start)
            )
            .order_by("-effective_from")
            .first()
        )

        available_hours = (
            capacity.weekly_available_hours
            if capacity
            else cls.DEFAULT_WEEKLY_HOURS
        )

        # Find allocations active during this week
        week_end = week_start + timedelta(days=6)
        allocations = (
            ProjectAllocation.objects.filter(
                user_id=user_id,
                start_date__lte=week_end,
            )
            .filter(
                Q(end_date__isnull=True) | Q(end_date__gte=week_start)
            )
            .select_related("project", "role")
        )

        allocated_hours = cls.ZERO
        projects = []

        for alloc in allocations:
            hours = Decimal(str(alloc.weekly_hours or 0))
            allocated_hours += hours
            projects.append(
                {
                    "project_code": alloc.project.code if alloc.project else "",
                    "project_name": alloc.project.name if alloc.project else "",
                    "weekly_hours": float(hours),
                    "role": str(alloc.role) if alloc.role else "",
                }
            )

        if available_hours > cls.ZERO:
            allocation_pct = (
                allocated_hours / available_hours * cls.HUNDRED
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            allocation_pct = cls.ZERO

        return {
            "available_hours": float(available_hours),
            "allocated_hours": float(allocated_hours),
            "allocation_pct": float(allocation_pct),
            "projects": projects,
        }

    @classmethod
    def detect_overload(cls, week_start: date = None) -> list:
        """
        Identify users whose allocated hours exceed their available hours
        for the given week.

        Args:
            week_start: Monday of the target week.  Defaults to the
                        current week's Monday.

        Returns:
            list of dicts, each with: user_id, username, full_name,
            available_hours, allocated_hours, overage_hours.
        """
        from apps.accounts.models import User

        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        overloaded = []
        active_users = User.objects.filter(is_active=True)

        for user in active_users:
            capacity_data = cls.get_user_capacity(user.id, week_start)
            if capacity_data["allocated_hours"] > capacity_data["available_hours"]:
                overloaded.append(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "full_name": user.get_full_name(),
                        "available_hours": capacity_data["available_hours"],
                        "allocated_hours": capacity_data["allocated_hours"],
                        "overage_hours": round(
                            capacity_data["allocated_hours"]
                            - capacity_data["available_hours"],
                            2,
                        ),
                    }
                )

        return overloaded

    @classmethod
    def detect_underload(
        cls, week_start: date = None, threshold_pct: Decimal = Decimal("50")
    ) -> list:
        """
        Identify users whose allocation percentage is below the given
        threshold for the specified week.

        Args:
            week_start:     Monday of the target week.  Defaults to the
                            current week's Monday.
            threshold_pct:  Percentage below which a user is considered
                            underloaded.  Default 50%.

        Returns:
            list of dicts, each with: user_id, username, full_name,
            available_hours, allocated_hours, allocation_pct.
        """
        from apps.accounts.models import User

        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        threshold = float(threshold_pct)
        underloaded = []
        active_users = User.objects.filter(is_active=True)

        for user in active_users:
            capacity_data = cls.get_user_capacity(user.id, week_start)
            if capacity_data["allocation_pct"] < threshold:
                underloaded.append(
                    {
                        "user_id": user.id,
                        "username": user.username,
                        "full_name": user.get_full_name(),
                        "available_hours": capacity_data["available_hours"],
                        "allocated_hours": capacity_data["allocated_hours"],
                        "allocation_pct": capacity_data["allocation_pct"],
                    }
                )

        return underloaded

    @classmethod
    @transaction.atomic
    def generate_alerts(cls, week_start: date = None) -> None:
        """
        Create CapacityAlert records for overloaded and underloaded users
        for the given week.

        Existing unresolved alerts for the same user/week are skipped
        to avoid duplicates.

        Args:
            week_start: Monday of the target week.  Defaults to the
                        current week's Monday.
        """
        from apps.capacity.models import CapacityAlert

        if week_start is None:
            today = date.today()
            week_start = today - timedelta(days=today.weekday())

        # Process overloaded users
        overloaded = cls.detect_overload(week_start)
        for entry in overloaded:
            exists = CapacityAlert.objects.filter(
                user_id=entry["user_id"],
                alert_type=CapacityAlert.AlertType.OVERLOAD,
                week_start=week_start,
                is_resolved=False,
            ).exists()

            if not exists:
                CapacityAlert.objects.create(
                    user_id=entry["user_id"],
                    alert_type=CapacityAlert.AlertType.OVERLOAD,
                    week_start=week_start,
                    allocated_hours=Decimal(str(entry["allocated_hours"])),
                    available_hours=Decimal(str(entry["available_hours"])),
                    details=(
                        f"Sobrecarga de {entry['overage_hours']}h. "
                        f"Asignadas: {entry['allocated_hours']}h, "
                        f"Disponibles: {entry['available_hours']}h."
                    ),
                )

        # Process underloaded users
        underloaded = cls.detect_underload(week_start)
        for entry in underloaded:
            exists = CapacityAlert.objects.filter(
                user_id=entry["user_id"],
                alert_type=CapacityAlert.AlertType.UNDERLOAD,
                week_start=week_start,
                is_resolved=False,
            ).exists()

            if not exists:
                CapacityAlert.objects.create(
                    user_id=entry["user_id"],
                    alert_type=CapacityAlert.AlertType.UNDERLOAD,
                    week_start=week_start,
                    allocated_hours=Decimal(str(entry["allocated_hours"])),
                    available_hours=Decimal(str(entry["available_hours"])),
                    details=(
                        f"Subcarga al {entry['allocation_pct']}%. "
                        f"Asignadas: {entry['allocated_hours']}h, "
                        f"Disponibles: {entry['available_hours']}h."
                    ),
                )


class AllocationService:
    """Operations for managing project allocations."""

    ZERO = Decimal("0")
    HUNDRED = Decimal("100")
    DEFAULT_WEEKLY_HOURS = Decimal("40")

    @staticmethod
    @transaction.atomic
    def allocate_user(
        user_id: int,
        project_id: int,
        role_id: int,
        start_date: date,
        end_date: date,
        weekly_hours: Decimal,
    ):
        """
        Create a new ProjectAllocation for a user on a project.

        The allocation_pct is computed automatically based on the user's
        current available hours.

        Args:
            user_id:      PK of the User.
            project_id:   PK of the Project.
            role_id:      PK of the Role.
            start_date:   When the allocation begins.
            end_date:     When the allocation ends.
            weekly_hours: Hours per week to allocate.

        Returns:
            The created ProjectAllocation instance.
        """
        from apps.capacity.models import ProjectAllocation, TeamMemberCapacity

        # Determine available hours to compute allocation percentage
        capacity = (
            TeamMemberCapacity.objects.filter(
                user_id=user_id,
                effective_from__lte=start_date,
            )
            .filter(
                Q(effective_until__isnull=True)
                | Q(effective_until__gte=start_date)
            )
            .order_by("-effective_from")
            .first()
        )

        available = (
            capacity.weekly_available_hours
            if capacity
            else AllocationService.DEFAULT_WEEKLY_HOURS
        )

        weekly_hours_dec = Decimal(str(weekly_hours))
        if available > AllocationService.ZERO:
            allocation_pct = (
                weekly_hours_dec / available * AllocationService.HUNDRED
            ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
        else:
            allocation_pct = AllocationService.ZERO

        allocation = ProjectAllocation.objects.create(
            user_id=user_id,
            project_id=project_id,
            role_id=role_id,
            start_date=start_date,
            end_date=end_date,
            weekly_hours=weekly_hours_dec,
            allocation_pct=allocation_pct,
        )

        return allocation

    @classmethod
    def get_allocation_matrix(cls, week_start: date) -> list:
        """
        Build an allocation matrix for all active users for the given week.

        Returns:
            list of dicts, each with:
                user          -- {id, username, full_name}
                projects      -- list of {project_code, project_name, hours, pct}
                total_hours   -- sum of allocated hours
                total_pct     -- sum of allocation percentages
        """
        from apps.accounts.models import User

        active_users = User.objects.filter(is_active=True).order_by(
            "first_name", "last_name"
        )
        matrix = []

        for user in active_users:
            capacity_data = CapacityService.get_user_capacity(
                user.id, week_start
            )
            available = capacity_data["available_hours"]

            project_entries = []
            for proj in capacity_data["projects"]:
                hours = proj["weekly_hours"]
                pct = round(hours / available * 100, 2) if available > 0 else 0
                project_entries.append(
                    {
                        "project_code": proj["project_code"],
                        "project_name": proj["project_name"],
                        "hours": hours,
                        "pct": pct,
                    }
                )

            matrix.append(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "full_name": user.get_full_name(),
                    },
                    "projects": project_entries,
                    "total_hours": capacity_data["allocated_hours"],
                    "total_pct": capacity_data["allocation_pct"],
                }
            )

        return matrix

    @classmethod
    def simulate_new_project(cls, project_hours: dict) -> dict:
        """
        Simulate the impact of adding a new project on team capacity.

        Args:
            project_hours: dict mapping user_id (int) to weekly_hours (float)
                           for the hypothetical new project.

        Returns:
            dict with:
                users -- list of dicts per affected user:
                    user_id, username, full_name,
                    current_allocated, new_allocated,
                    available, new_allocation_pct,
                    would_overload (bool)
                total_overloaded -- count of users who would exceed capacity
        """
        from apps.accounts.models import User

        today = date.today()
        week_start = today - timedelta(days=today.weekday())

        results = []
        total_overloaded = 0

        for user_id, extra_hours in project_hours.items():
            user_id = int(user_id)
            extra = float(extra_hours)

            try:
                user = User.objects.get(pk=user_id)
            except User.DoesNotExist:
                continue

            capacity_data = CapacityService.get_user_capacity(
                user_id, week_start
            )
            new_allocated = capacity_data["allocated_hours"] + extra
            available = capacity_data["available_hours"]
            new_pct = round(new_allocated / available * 100, 2) if available > 0 else 0
            would_overload = new_allocated > available

            if would_overload:
                total_overloaded += 1

            results.append(
                {
                    "user_id": user_id,
                    "username": user.username,
                    "full_name": user.get_full_name(),
                    "current_allocated": capacity_data["allocated_hours"],
                    "new_allocated": round(new_allocated, 2),
                    "available": available,
                    "new_allocation_pct": new_pct,
                    "would_overload": would_overload,
                }
            )

        return {
            "users": results,
            "total_overloaded": total_overloaded,
        }
