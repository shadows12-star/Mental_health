

# Create your views here.

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)

from .forms import AssessmentForm
from .models import Assessment
from .ml_service import (
    predict_mental_health,
    metadata,
)

logger = logging.getLogger(__name__)


@login_required
def assessment_create(request):

    if request.method == "POST":
        form = AssessmentForm(request.POST)

        if form.is_valid():
            assessment = form.save(commit=False)

            data = {
                "Age": assessment.age,
                "Gender": assessment.gender,
                "Country": assessment.country.strip(),
                "Academic_Level": assessment.academic_level,
                "Most_Used_Platform":
                    assessment.most_used_platform,
                "Purpose_Of_Use":
                    assessment.purpose_of_use,
                "Avg_Daily_Usage_Hours":
                    assessment.avg_daily_usage_hours,
                "Daily_Unlocks":
                    assessment.daily_unlocks,
                "Physical_Activity_Hours":
                    assessment.physical_activity_hours,
                "Sleep_Hours_Per_Night":
                    assessment.sleep_hours_per_night,
                "Study_Hours":
                    assessment.study_hours,
                "Stress_Level":
                    assessment.stress_level,
            }

            try:
                predicted_score = (
                    predict_mental_health(data)
                )
            except (ValueError, KeyError, TypeError):
                logger.exception(
                    "Assessment prediction failed"
                )
                form.add_error(
                    None,
                    "The prediction could not be completed. "
                    "Please review your answers."
                )
            else:
                assessment.user = request.user
                assessment.predicted_score = (
                    predicted_score
                )
                assessment.model_version = metadata.get(
                    "model_version", "1.0"
                )

                assessment.save()

                return redirect(
                    "assessment_result",
                    pk=assessment.pk
                )

    else:
        form = AssessmentForm()

    return render(
        request,
        "assessments/assessment_form.html",
        {"form": form}
    )


@login_required
def assessment_result(request, pk):

    assessment = get_object_or_404(
        Assessment,
        pk=pk,
        user=request.user
    )

    return render(
        request,
        "assessments/assessment_result.html",
        {"assessment": assessment}
    )


@login_required
def assessment_history(request):

    assessments = Assessment.objects.filter(
        user=request.user
    )

    return render(
        request,
        "assessments/assessment_history.html",
        {"assessments": assessments}
    )
