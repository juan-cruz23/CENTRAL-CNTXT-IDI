from apps.common.models import AuditLog


class AuditMixin:
    """
    Mixin that automatically creates AuditLog entries on save and delete.

    To track the user and IP address, set `_audit_user` and `_audit_ip`
    attributes on the model instance before calling save() or delete().
    """

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        action = AuditLog.Action.CREATE if is_new else AuditLog.Action.UPDATE

        # Capture changes for updates
        changes = {}
        if not is_new:
            try:
                old_instance = self.__class__.objects.get(pk=self.pk)
                for field in self._meta.fields:
                    old_value = getattr(old_instance, field.attname)
                    new_value = getattr(self, field.attname)
                    if old_value != new_value:
                        changes[field.name] = {
                            "old": str(old_value),
                            "new": str(new_value),
                        }
            except self.__class__.DoesNotExist:
                pass

        super().save(*args, **kwargs)

        AuditLog.objects.create(
            user=getattr(self, "_audit_user", None),
            action=action,
            model_name=self.__class__.__name__,
            object_id=str(self.pk),
            changes=changes,
            ip_address=getattr(self, "_audit_ip", None),
        )

    def delete(self, *args, **kwargs):
        AuditLog.objects.create(
            user=getattr(self, "_audit_user", None),
            action=AuditLog.Action.DELETE,
            model_name=self.__class__.__name__,
            object_id=str(self.pk),
            changes={},
            ip_address=getattr(self, "_audit_ip", None),
        )
        return super().delete(*args, **kwargs)
