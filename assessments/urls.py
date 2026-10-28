from django.urls import path
from . import views

urlpatterns = [
    path(
        "new/",
        views.assessment_create,
        name="assessment_create"
    ),
    path(
        "history/",
        views.assessment_history,
        name="assessment_history"
    ),
    path(
        "result/<int:pk>/",
        views.assessment_result,
        name="assessment_result"
    ),
]