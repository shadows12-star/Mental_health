
from django import forms

from .models import Assessment
from .ml_service import model, metadata


def get_category_choices(feature_name):
    """
    Read fitted categories from the saved
    preprocessing pipeline.
    """
    preprocessor = model.named_steps["preprocessor"]

    encoder = (
        preprocessor
        .named_transformers_["normal"]
        .named_steps["one_hot_encoder"]
    )

    # Must match the normal_cols order
    feature_names = [
        "Grouped_country",
        "Most_Used_Platform",
        "Gender",
        "Academic_Level",
        "Purpose_Of_Use",
    ]

    index = feature_names.index(feature_name)

    categories = encoder.categories_[index]

    return [
        (str(value), str(value))
        for value in categories
    ]


class AssessmentForm(forms.ModelForm):

    gender = forms.ChoiceField(
        choices=get_category_choices("Gender")
    )

    academic_level = forms.ChoiceField(
        choices=get_category_choices("Academic_Level")
    )

    most_used_platform = forms.ChoiceField(
        choices=get_category_choices("Most_Used_Platform")
    )

    purpose_of_use = forms.ChoiceField(
        choices=get_category_choices("Purpose_Of_Use")
    )

    stress_level = forms.ChoiceField(
        choices=[
            ("Low", "Low"),
            ("Medium", "Medium"),
            ("High", "High"),
            ("Very High", "Very High"),
        ]
    )

    country = forms.CharField(
        max_length=100,
        help_text=(
            "Enter your country. Countries outside "
            "the model's main groups are categorized "
            "as Other."
        )
    )

    class Meta:
        model = Assessment

        fields = [
            "age",
            "gender",
            "country",
            "academic_level",
            "most_used_platform",
            "purpose_of_use",
            "avg_daily_usage_hours",
            "daily_unlocks",
            "physical_activity_hours",
            "sleep_hours_per_night",
            "study_hours",
            "stress_level",
        ]

        labels = {
            "avg_daily_usage_hours":
                "Daily Social Media Usage (Hours)",
            "daily_unlocks":
                "Phone Unlocks Per Day",
            "physical_activity_hours":
                "Daily Physical Activity (Hours)",
            "sleep_hours_per_night":
                "Sleep Hours Per Night",
            "study_hours":
                "Daily Study Hours",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"

        # Basic sanity limits; not clinical thresholds.
        self.fields["age"].min_value = 13
        self.fields["age"].max_value = 100

        self.fields["daily_unlocks"].min_value = 0

        for name in [
            "avg_daily_usage_hours",
            "physical_activity_hours",
            "sleep_hours_per_night",
            "study_hours",
        ]:
            self.fields[name].min_value = 0
            self.fields[name].max_value = 24
