import numpy as np
from app.ml.model_loader import get_model
from app.models.prediction_result import AlcoholismRisk

def run_inference(X: np.ndarray) -> tuple[AlcoholismRisk, float, float]:
    model = get_model()
    preds = model.predict(X, verbose=0)

    mean_prob = float(np.mean(preds))
    is_alcoholic = mean_prob >= 0.5

    label = AlcoholismRisk.ALCOHOLIC if is_alcoholic else AlcoholismRisk.NON_ALCOHOLIC
    confidence = mean_prob if is_alcoholic else 1.0 - mean_prob

    return label, mean_prob, confidence
