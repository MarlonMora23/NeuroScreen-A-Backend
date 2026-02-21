import time
from app.extensions import db, celery
from app.domain.reader.parquet_reader import ParquetEegReader
from app.ml.inference import run_inference
from app.ml.model_loader import get_model
from app.models.eeg_record import EegRecord, EegStatus
from app.models.prediction_result import PredictionResult
from app.ml.preprocessing import build_tensor_from_parquet

@celery.task(bind=True, max_retries=3)
def process_eeg_record(self, eeg_record_id: int):
    start_time = time.time()

    eeg_record = db.session.get(EegRecord, eeg_record_id)
    if not eeg_record:
        # No tiene sentido reintentar si el registro no existe
        return {"error": f"EegRecord {eeg_record_id} not found"}

    try:
        eeg_record.status = EegStatus.PROCESSING
        db.session.commit()

        X = build_tensor_from_parquet(
            parquet_path=eeg_record.file_path,
            win_size=256,
            step_size=256,
            use_bands=True
        )

        if X.size == 0:
            raise ValueError("No valid EEG samples generated from the provided file")

        label, raw_prob, confidence = run_inference(X)

        prediction = PredictionResult(
            eeg_record_id=eeg_record.id,
            result=label,
            confidence=confidence,
            raw_probability=raw_prob,       
            model_version="eegnet_v1"
        )

        db.session.add(prediction)

        eeg_record.status = EegStatus.PROCESSED
        eeg_record.processing_time_ms = int((time.time() - start_time) * 1000)
        eeg_record.error_msg = None  # limpiar errores de intentos previos

        db.session.commit()

        return {"eeg_record_id": eeg_record_id, "status": "processed"}

    except Exception as e:
        db.session.rollback()  # importante: revertir cualquier cambio parcial

        eeg_record.status = EegStatus.FAILED
        eeg_record.error_msg = str(e)[:500]  # limitar longitud para no llenar la BD

        try:
            db.session.commit()
        except Exception:
            db.session.rollback()

        raise self.retry(exc=e, countdown=60)  # reintenta tras 60s, máximo 3 veces