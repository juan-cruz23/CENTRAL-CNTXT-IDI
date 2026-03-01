from django import template

from apps.accounts.models import UserRole

register = template.Library()


@register.simple_tag
def user_roles(user):
    """
    Return the roles assigned to a given user.

    Usage in templates:
        {% load accounts_tags %}
        {% user_roles request.user as roles %}
        {% for user_role in roles %}
            {{ user_role.role.name }}
        {% endfor %}
    """
    if user is None or not user.is_authenticated:
        return UserRole.objects.none()
    return UserRole.objects.filter(user=user).select_related("role")
