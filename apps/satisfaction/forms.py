from django import forms

from apps.common.forms import DaisyUIFormMixin
from apps.satisfaction.models import SatisfactionMeasurement, SatisfactionSurvey


class SatisfactionMeasurementForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = SatisfactionMeasurement
        fields = [
            "project",
            "milestone",
            "measurement_date",
            "observed_emotion_pct",
            "spontaneous_phrase_pct",
            "audio_video_link",
            "symbolic_object_pct",
            "notes",
        ]
        widgets = {
            "project": forms.Select(attrs={"class": "form-select"}),
            "milestone": forms.Select(attrs={"class": "form-select"}),
            "measurement_date": forms.DateInput(
                attrs={"class": "form-control", "type": "date"}
            ),
            "observed_emotion_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "spontaneous_phrase_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "audio_video_link": forms.URLInput(attrs={"class": "form-control"}),
            "symbolic_object_pct": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }


class SatisfactionSurveyForm(DaisyUIFormMixin, forms.ModelForm):
    class Meta:
        model = SatisfactionSurvey
        fields = [
            "general_sensation",
            "clarity_and_support",
            "personal_effort",
            "team_relationship",
            "confidence",
            "perceived_value",
            "notes",
        ]
        widgets = {
            "general_sensation": forms.NumberInput(attrs={"class": "form-control"}),
            "clarity_and_support": forms.NumberInput(attrs={"class": "form-control"}),
            "personal_effort": forms.NumberInput(attrs={"class": "form-control"}),
            "team_relationship": forms.NumberInput(attrs={"class": "form-control"}),
            "confidence": forms.NumberInput(attrs={"class": "form-control"}),
            "perceived_value": forms.NumberInput(attrs={"class": "form-control"}),
            "notes": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
        }
