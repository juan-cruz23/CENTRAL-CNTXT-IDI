from decimal import Decimal

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


# ---------------------------------------------------------------------------
# Status badge
# ---------------------------------------------------------------------------
STATUS_CSS_CLASSES = {
    "PLANNING": "bg-blue-100 text-blue-800",
    "ACTIVE": "bg-green-100 text-green-800",
    "PAUSED": "bg-yellow-100 text-yellow-800",
    "COMPLETED": "bg-gray-100 text-gray-800",
    "CANCELLED": "bg-red-100 text-red-800",
}


@register.filter(name="status_badge")
def status_badge(status):
    """
    Return a CSS class string suitable for a Tailwind badge based on project status.

    Usage in templates:
        <span class="{{ project.status|status_badge }}">{{ project.get_status_display }}</span>
    """
    if not status:
        return "bg-gray-100 text-gray-800"
    return STATUS_CSS_CLASSES.get(str(status).upper(), "bg-gray-100 text-gray-800")


# ---------------------------------------------------------------------------
# Progress bar
# ---------------------------------------------------------------------------
@register.simple_tag(name="progress_bar")
def progress_bar(value, max_value=100, height="h-2", show_label=False):
    """
    Return an HTML progress bar based on a percentage value.

    Usage in templates:
        {% load project_tags %}
        {% progress_bar project.current_progress_pct %}
        {% progress_bar service.progress_pct 100 "h-4" True %}

    Args:
        value: The current progress value (0-100).
        max_value: The maximum value (default 100).
        height: Tailwind height class for the bar (default "h-2").
        show_label: Whether to show the percentage label (default False).
    """
    try:
        pct = float(Decimal(str(value))) if value else 0.0
        max_val = float(Decimal(str(max_value))) if max_value else 100.0
    except Exception:
        pct = 0.0
        max_val = 100.0

    if max_val > 0:
        width_pct = min((pct / max_val) * 100, 100)
    else:
        width_pct = 0

    # Choose colour based on progress
    if width_pct >= 80:
        bar_color = "bg-green-500"
    elif width_pct >= 50:
        bar_color = "bg-yellow-500"
    elif width_pct >= 25:
        bar_color = "bg-orange-500"
    else:
        bar_color = "bg-red-500"

    label_html = ""
    if show_label:
        label_html = (
            f'<span class="ml-2 text-sm font-medium text-gray-700">'
            f"{width_pct:.1f}%</span>"
        )

    html = (
        f'<div class="flex items-center">'
        f'<div class="w-full bg-gray-200 rounded-full {height}">'
        f'<div class="{bar_color} {height} rounded-full" '
        f'style="width: {width_pct:.1f}%"></div>'
        f"</div>"
        f"{label_html}"
        f"</div>"
    )
    return mark_safe(html)
