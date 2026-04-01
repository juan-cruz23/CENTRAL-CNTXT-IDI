from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.geography.models import Country, Municipality


class CountryForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Country
        fields = ["name", "iso_code", "is_active"]


class MunicipalityForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = Municipality
        fields = ["name", "department", "country", "is_active"]
