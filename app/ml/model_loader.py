import threading
from tensorflow import keras

_model = None
_model_lock = threading.Lock()
MODEL_PATH = "dl_models/eegnet_model.keras"

def get_model():
    global _model
    if _model is None:
        with _model_lock:
            if _model is None:  # double-checked locking
                _model = keras.models.load_model(MODEL_PATH)
    return _model