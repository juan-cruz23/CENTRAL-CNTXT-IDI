from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.views.generic import CreateView, TemplateView

from apps.projects.models import Project
from apps.satisfaction.forms import SatisfactionMeasurementForm, SatisfactionSurveyForm
from apps.satisfaction.models import SatisfactionMeasurement, SatisfactionSurvey


class ProjectSatisfactionView(LoginRequiredMixin, TemplateView):
    """Shows CVE + Survey data for a project, with radar chart placeholder."""

    template_name = "satisfaction/project_satisfaction.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        measurements = (
            SatisfactionMeasurement.objects.filter(project=project)
            .select_related("milestone")
            .prefetch_related("survey")
        )

        context["project"] = project
        context["measurements"] = measurements

        # Prepare radar chart data from the latest survey if available
        latest = measurements.first()
        if latest and hasattr(latest, "survey"):
            survey = latest.survey
            context["radar_data"] = {
                "labels": [
                    "Sensación general",
                    "Claridad y acompañamiento",
                    "Esfuerzo personal",
                    "Relación con el equipo",
                    "Confianza",
                    "Valor percibido",
                ],
                "values": [
                    float(survey.general_sensation),
                    float(survey.clarity_and_support),
                    float(survey.personal_effort),
                    float(survey.team_relationship),
                    float(survey.confidence),
                    float(survey.perceived_value),
                ],
            }

        return context


class CVECreateView(LoginRequiredMixin, CreateView):
    """Form for leaders to record a CVE measurement."""

    model = SatisfactionMeasurement
    form_class = SatisfactionMeasurementForm
    template_name = "satisfaction/cve_create.html"

    def get_initial(self):
        initial = super().get_initial()
        initial["project"] = self.kwargs["project_pk"]
        return initial

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context

    def get_success_url(self):
        return reverse(
            "satisfaction:project_satisfaction",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )


class SurveyCreateView(LoginRequiredMixin, CreateView):
    """Creates a survey linked to a measurement."""

    model = SatisfactionSurvey
    form_class = SatisfactionSurveyForm
    template_name = "satisfaction/survey_create.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["project"] = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        return context

    def form_valid(self, form):
        # Link survey to the latest measurement for this project if not already set
        project = get_object_or_404(Project, pk=self.kwargs["project_pk"])
        measurement = SatisfactionMeasurement.objects.filter(
            project=project,
        ).first()
        if measurement:
            form.instance.measurement = measurement
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "satisfaction:project_satisfaction",
            kwargs={"project_pk": self.kwargs["project_pk"]},
        )


class PublicSurveyView(CreateView):
    """Public form (no login required) for client satisfaction survey."""

    model = SatisfactionSurvey
    form_class = SatisfactionSurveyForm
    template_name = "satisfaction/public_survey.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["token"] = self.kwargs["token"]
        return context

    def form_valid(self, form):
        # Look up the measurement by the token (UUID used as lookup)
        measurement = get_object_or_404(
            SatisfactionMeasurement,
            pk=self.kwargs["token"],
        )
        form.instance.measurement = measurement
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            "satisfaction:public_survey",
            kwargs={"token": self.kwargs["token"]},
        )
