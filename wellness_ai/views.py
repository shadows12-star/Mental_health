
import json
import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import (
    get_object_or_404,
    redirect,
    render,
)
from django.views.decorators.http import (
    require_GET,
    require_POST,
)

from assessments.models import Assessment

from .models import WellnessRecommendation
from .services import (
    generate_wellness_guidance,
    FALLBACK_MESSAGE,
)
from .chat_service import (
    send_chat_message,
    get_chat_history,
)


logger = logging.getLogger(__name__)


# --------------------------------------
# PHASE 5: AI WELLNESS RECOMMENDATIONS
# --------------------------------------

@login_required
@require_POST
def generate_recommendation_view(request, assessment_id):

    assessment = get_object_or_404(
        Assessment,
        pk=assessment_id,
        user=request.user
    )

    # Reuse an existing recommendation
    if WellnessRecommendation.objects.filter(
        assessment=assessment
    ).exists():
        return redirect(
            "assessment_result",
            pk=assessment.pk
        )

    guidance, sources = generate_wellness_guidance(
        assessment
    )

    # Don't permanently store API failure messages.
    if guidance == FALLBACK_MESSAGE:
        messages.warning(
            request,
            "AI recommendations are temporarily "
            "unavailable. Please try again."
        )

        return redirect(
            "assessment_result",
            pk=assessment.pk
        )

    WellnessRecommendation.objects.get_or_create(
        assessment=assessment,
        defaults={
            "user": request.user,
            "content": guidance,
            "sources": sources,
        }
    )

    messages.success(
        request,
        "Your wellness recommendations are ready!"
    )

    return redirect(
        "assessment_result",
        pk=assessment.pk
    )


# --------------------------------------
# PHASE 6: LANGGRAPH CHATBOT
# --------------------------------------

@login_required
@require_GET
def chat_page(request):
    """
    Display the chatbot with the latest
    saved conversation from SQLite.
    """

    try:
        history = get_chat_history(request.user)

    except Exception:
        logger.exception(
            "Failed to load chatbot history"
        )

        history = []

        messages.error(
            request,
            "Unable to load previous messages."
        )

    return render(
        request,
        "wellness_ai/chat.html",
        {
            "chat_messages": history,
        }
    )


@login_required
@require_POST
def send_message(request):
    """
    Receive a message, invoke the LangGraph
    agent, and return its response as JSON.
    """

    try:
        payload = json.loads(
            request.body.decode("utf-8")
        )

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse(
            {"error": "Invalid JSON request."},
            status=400
        )

    if not isinstance(payload, dict):
        return JsonResponse(
            {"error": "Invalid request format."},
            status=400
        )

    user_message = payload.get("message", "")

    if not isinstance(user_message, str):
        return JsonResponse(
            {"error": "Message must be text."},
            status=400
        )

    user_message = user_message.strip()

    if not user_message:
        return JsonResponse(
            {"error": "Please enter a message."},
            status=400
        )

    if len(user_message) > 1500:
        return JsonResponse(
            {"error": "Message is too long (max 1500 characters)."},
            status=400
        )

    try:
        response = send_chat_message(
            user=request.user,
            message=user_message
        )

    except Exception:
        logger.exception(
            "Failed to process chat message"
        )

        return JsonResponse(
            {"error": "Unable to process your message."},
            status=503
        )

    if not isinstance(response, str) or not response.strip():
        return JsonResponse(
            {"error": "The assistant returned an empty response."},
            status=503
        )

    return JsonResponse({
        "response": response,
    })
