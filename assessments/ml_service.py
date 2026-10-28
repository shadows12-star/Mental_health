
import json
from pathlib import Path

import joblib
import pandas as pd
from django.conf import settings


MODEL_DIR = Path(settings.BASE_DIR) / "ml_models"

MODEL_PATH = MODEL_DIR / "mental_health_pipeline.joblib"
METADATA_PATH = MODEL_DIR / "model_metadata.json"


# Load trained ML pipeline
model = joblib.load(MODEL_PATH)

# Load metadata
with open(METADATA_PATH, "r", encoding="utf-8") as f:
    metadata = json.load(f)


def predict_mental_health(user_data):
    """
    Predict an experimental mental health score
    from user assessment responses.
    """

    data = user_data.copy()

    # Apply country grouping from training
    country = data.pop("Country")

    if country in metadata["top_countries"]:
        data["Grouped_country"] = country
    else:
        data["Grouped_country"] = "Other"

    # Match original training feature order
    df = pd.DataFrame(
        [data],
        columns=metadata["feature_columns"]
    )

    # Predict
    prediction = model.predict(df)[0]

    return round(float(prediction), 2)
