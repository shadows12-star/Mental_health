
from django.urls import path
from . import views

urlpatterns = [
    # Phase 5: AI recommendations
    path(
        "generate/<int:assessment_id>/",
        views.generate_recommendation_view,
        name="generate_recommendation",
    ),

    # Phase 6: LangGraph chatbot
    path(
        "chat/",
        views.chat_page,
        name="chat_home",
    ),

    path(
        "chat/send/",
        views.send_message,
        name="chat_send",
    ),
]
