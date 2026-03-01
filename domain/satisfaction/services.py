"""
Domain services for client satisfaction tracking.

Manages CVE (Calidad de Valor Emocional) measurements and assertiveness
surveys, and produces chart-ready data for radar visualisations.
"""

from datetime import date


class SatisfactionService:
    """Operations for recording and querying satisfaction metrics."""

    @staticmethod
    def record_cve(
        project_id: int,
        milestone_id: int = None,
        emotion_pct: float = 0,
        phrase_pct: float = 0,
        audio_link: str = "",
        symbolic_pct: float = 0,
    ):
        """
        Create a new CVE (Calidad de Valor Emocional) measurement for a project.

        The model's save() method automatically computes cve_score as the
        average of the three dimension percentages.

        Args:
            project_id:   PK of the Project.
            milestone_id: Optional PK of the associated Milestone.
            emotion_pct:  Observed emotion percentage (0-100).
            phrase_pct:   Spontaneous phrase percentage (0-100).
            audio_link:   URL to audio/video evidence.
            symbolic_pct: Symbolic object percentage (0-100).

        Returns:
            The created SatisfactionMeasurement instance.
        """
        from apps.satisfaction.models import SatisfactionMeasurement

        measurement = SatisfactionMeasurement(
            project_id=project_id,
            milestone_id=milestone_id,
            measurement_date=date.today(),
            observed_emotion_pct=emotion_pct,
            spontaneous_phrase_pct=phrase_pct,
            audio_video_link=audio_link,
            symbolic_object_pct=symbolic_pct,
        )
        # save() computes cve_score automatically
        measurement.save()
        return measurement

    @staticmethod
    def record_survey(measurement_id: int, scores: dict):
        """
        Create or update an assertiveness survey linked to a CVE measurement.

        The model's save() method automatically computes total_score_pct
        as the average of the six dimension fields.

        Args:
            measurement_id: PK of the parent SatisfactionMeasurement.
            scores: dict with keys matching the survey dimension fields:
                general_sensation, clarity_and_support, personal_effort,
                team_relationship, confidence, perceived_value.

        Returns:
            The created or updated SatisfactionSurvey instance.
        """
        from apps.satisfaction.models import SatisfactionSurvey

        survey_fields = {
            "general_sensation",
            "clarity_and_support",
            "personal_effort",
            "team_relationship",
            "confidence",
            "perceived_value",
        }

        defaults = {
            k: v for k, v in scores.items() if k in survey_fields
        }

        survey, _created = SatisfactionSurvey.objects.update_or_create(
            measurement_id=measurement_id,
            defaults=defaults,
        )
        # Re-save to trigger the score computation in case update_or_create
        # did not call the custom save logic for updates.
        survey.save()
        return survey

    @staticmethod
    def get_project_satisfaction(project_id: int) -> dict:
        """
        Retrieve a comprehensive satisfaction overview for a project.

        Returns:
            dict with keys:
                cve_scores    -- list of {date, score, emotion, phrase, symbolic}
                survey_scores -- list of {date, total_score_pct, dimensions...}
                latest_cve    -- most recent CVE dict or None
                latest_survey -- most recent survey dict or None
                radar_data    -- output of get_radar_data()
        """
        from apps.satisfaction.models import SatisfactionMeasurement

        measurements = SatisfactionMeasurement.objects.filter(
            project_id=project_id
        ).order_by("measurement_date")

        cve_scores = []
        survey_scores = []
        latest_cve = None
        latest_survey = None

        for m in measurements:
            cve_entry = {
                "id": m.id,
                "date": m.measurement_date,
                "score": float(m.cve_score or 0),
                "emotion": float(m.observed_emotion_pct or 0),
                "phrase": float(m.spontaneous_phrase_pct or 0),
                "symbolic": float(m.symbolic_object_pct or 0),
            }
            cve_scores.append(cve_entry)
            latest_cve = cve_entry

            # Check for linked survey
            try:
                survey = m.survey
                survey_entry = {
                    "id": survey.id,
                    "date": m.measurement_date,
                    "total_score_pct": float(survey.total_score_pct or 0),
                    "general_sensation": float(survey.general_sensation or 0),
                    "clarity_and_support": float(survey.clarity_and_support or 0),
                    "personal_effort": float(survey.personal_effort or 0),
                    "team_relationship": float(survey.team_relationship or 0),
                    "confidence": float(survey.confidence or 0),
                    "perceived_value": float(survey.perceived_value or 0),
                }
                survey_scores.append(survey_entry)
                latest_survey = survey_entry
            except Exception:
                # No survey linked to this measurement
                pass

        radar_data = SatisfactionService.get_radar_data(project_id)

        return {
            "cve_scores": cve_scores,
            "survey_scores": survey_scores,
            "latest_cve": latest_cve,
            "latest_survey": latest_survey,
            "radar_data": radar_data,
        }

    @staticmethod
    def get_radar_data(project_id: int) -> dict:
        """
        Generate radar chart data for Chart.js visualisation.

        Computes the average across all measurements for each CVE
        dimension and each survey dimension.

        Returns:
            dict with keys:
                labels       -- list of dimension label strings
                cve_values   -- list of average values for CVE dimensions
                survey_values -- list of average values for survey dimensions
        """
        from apps.satisfaction.models import SatisfactionMeasurement

        measurements = SatisfactionMeasurement.objects.filter(
            project_id=project_id
        ).order_by("measurement_date")

        if not measurements.exists():
            return {
                "labels": [],
                "cve_values": [],
                "survey_values": [],
            }

        # CVE dimension accumulators
        emotion_total = 0.0
        phrase_total = 0.0
        symbolic_total = 0.0
        cve_count = 0

        # Survey dimension accumulators
        sensation_total = 0.0
        clarity_total = 0.0
        effort_total = 0.0
        relationship_total = 0.0
        confidence_total = 0.0
        value_total = 0.0
        survey_count = 0

        for m in measurements:
            emotion_total += float(m.observed_emotion_pct or 0)
            phrase_total += float(m.spontaneous_phrase_pct or 0)
            symbolic_total += float(m.symbolic_object_pct or 0)
            cve_count += 1

            try:
                survey = m.survey
                sensation_total += float(survey.general_sensation or 0)
                clarity_total += float(survey.clarity_and_support or 0)
                effort_total += float(survey.personal_effort or 0)
                relationship_total += float(survey.team_relationship or 0)
                confidence_total += float(survey.confidence or 0)
                value_total += float(survey.perceived_value or 0)
                survey_count += 1
            except Exception:
                pass

        # Compute CVE averages
        if cve_count > 0:
            cve_values = [
                round(emotion_total / cve_count, 2),
                round(phrase_total / cve_count, 2),
                round(symbolic_total / cve_count, 2),
            ]
        else:
            cve_values = [0.0, 0.0, 0.0]

        # Compute survey averages
        if survey_count > 0:
            survey_values = [
                round(sensation_total / survey_count, 2),
                round(clarity_total / survey_count, 2),
                round(effort_total / survey_count, 2),
                round(relationship_total / survey_count, 2),
                round(confidence_total / survey_count, 2),
                round(value_total / survey_count, 2),
            ]
        else:
            survey_values = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

        labels = [
            "Emocion Observada",
            "Frase Espontanea",
            "Objeto Simbolico",
            "Sensacion General",
            "Claridad y Acompanamiento",
            "Esfuerzo Personal",
            "Relacion con Equipo",
            "Confianza",
            "Valor Percibido",
        ]

        return {
            "labels": labels,
            "cve_values": cve_values,
            "survey_values": survey_values,
        }
