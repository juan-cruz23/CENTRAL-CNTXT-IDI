"""
Google Calendar sync service.
Handles event fetching, project matching, and data aggregation.

Note: Actual Google Calendar API calls require google-api-python-client
and valid OAuth2 credentials. This module provides the matching/processing
logic that works with fetched event data.
"""

from datetime import date, timedelta
from decimal import Decimal

from django.db.models import Sum

from apps.calendar_sync.models import (
    CalendarEvent,
    ProjectColorMapping,
    ProjectKeywordMapping,
)
from apps.projects.models import Project


def match_event_to_project(user, title, color_id=None):
    """
    Try to match an event to a project using:
    1. Color mapping (if color_id provided)
    2. Keyword mapping (search title)
    3. Project code/name in title

    Returns (project, match_method) or (None, 'UNMATCHED')
    """
    # 1. Color mapping
    if color_id:
        color_mapping = ProjectColorMapping.objects.filter(
            user=user,
            color_id=color_id,
        ).select_related("project").first()
        if color_mapping:
            return color_mapping.project, "AUTO_COLOR"

    # 2. Keyword mapping
    title_lower = title.lower()
    keyword_mappings = ProjectKeywordMapping.objects.select_related("project").all()
    for km in keyword_mappings:
        if km.keyword.lower() in title_lower:
            return km.project, "AUTO_NAME"

    # 3. Project code or name in title
    active_projects = Project.objects.filter(status="ACTIVE")
    for project in active_projects:
        if project.code.lower() in title_lower or project.name.lower() in title_lower:
            return project, "AUTO_NAME"

    return None, "UNMATCHED"


def get_weekly_calendar_summary(user, week_start):
    """Get hours by project for a given week."""
    week_end = week_start + timedelta(days=7)
    events = CalendarEvent.objects.filter(
        user=user,
        start_time__date__gte=week_start,
        start_time__date__lt=week_end,
        project__isnull=False,
    ).values("project__code", "project__name").annotate(
        total_hours=Sum("duration_hours"),
    ).order_by("-total_hours")

    return list(events)


def get_unmatched_events(user, days_back=14):
    """Get recent events not matched to any project."""
    since = date.today() - timedelta(days=days_back)
    return CalendarEvent.objects.filter(
        user=user,
        project__isnull=True,
        start_time__date__gte=since,
    ).order_by("-start_time")
