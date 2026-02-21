import numpy as np

from app.ml.model_loader import get_model

def run_inference(X: np.ndarray) -> tuple[bool, float]:
    model = get_model()
    preds = model.predict(X)

    mean_prob = float(np.mean(preds))

    label = mean_prob >= 0.5
    confidence = mean_prob if label else 1 - mean_prob

    return label, mean_prob, confidence
