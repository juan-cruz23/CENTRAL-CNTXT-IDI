"""Pricing permission mixins for service instances."""


def has_pricing_permission(user):
    """
    Check if a user has permission to modify pricing fields
    (unit_price, projected_hours, quantity).

    Returns True if:
    - User is staff (admin)
    - User has the DO (Dirección Operativa) role
    """
    if user.is_staff:
        return True

    return user.user_roles.filter(role__code="DO").exists()
