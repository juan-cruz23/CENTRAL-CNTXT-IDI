from apps.notifications.models import Alert


def unread_alerts(request):
    """
    Context processor that provides the unread alert count for the navbar badge.
    Returns {"unread_alert_count": <int>} for authenticated users, 0 otherwise.
    """
    if request.user.is_authenticated:
        count = Alert.objects.filter(
            target_users=request.user,
            is_read=False,
        ).count()
        return {"unread_alert_count": count}
    return {"unread_alert_count": 0}
