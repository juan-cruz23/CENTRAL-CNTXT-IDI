from django import forms


class DaisyUIFormMixin:
    """
    Mixin that applies daisyUI CSS classes to all form widgets.
    Must be placed before the Form class in MRO.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get("class", "")
            if isinstance(widget, forms.CheckboxInput):
                widget.attrs["class"] = f"checkbox checkbox-primary {existing}".strip()
            elif isinstance(widget, forms.ClearableFileInput):
                widget.attrs["class"] = (
                    f"file-input file-input-bordered w-full {existing}".strip()
                )
            elif isinstance(widget, forms.Select):
                widget.attrs["class"] = (
                    f"select select-bordered w-full {existing}".strip()
                )
            elif isinstance(widget, forms.Textarea):
                widget.attrs["class"] = (
                    f"textarea textarea-bordered w-full {existing}".strip()
                )
            elif isinstance(widget, forms.DateInput):
                widget.attrs["class"] = (
                    f"input input-bordered w-full {existing}".strip()
                )
                widget.attrs.setdefault("type", "date")
            elif isinstance(
                widget, (forms.TextInput, forms.EmailInput, forms.URLInput,
                         forms.NumberInput, forms.PasswordInput)
            ):
                widget.attrs["class"] = (
                    f"input input-bordered w-full {existing}".strip()
                )
