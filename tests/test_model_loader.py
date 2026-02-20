import numpy as np
from app.ml import model_loader, inference


def test_get_model_monkeypatch(monkeypatch):
    calls = []

    class DummyModel:
        def predict(self, X):
            return np.array([0.2, 0.8])

    def fake_load(path):
        calls.append(path)
        return DummyModel()

    monkeypatch.setattr(model_loader.keras.models, 'load_model', fake_load)

    # First call should trigger load_model
    m = model_loader.get_model()
    assert m is not None

    # Second call should reuse cached model
    m2 = model_loader.get_model()
    assert m is m2
    assert calls == [model_loader.MODEL_PATH]


def test_run_inference_with_dummy_model(monkeypatch):
    class DummyModel:
        def predict(self, X):
            return np.array([0.3, 0.7])

    # Inject dummy model directly
    monkeypatch.setattr(model_loader, '_model', DummyModel())

    label, mean_prob, confidence = inference.run_inference(np.zeros((1, 10)))
    assert isinstance(label, (bool, np.bool_))
    assert 0.0 <= mean_prob <= 1.0
    assert 0.0 <= confidence <= 1.0
