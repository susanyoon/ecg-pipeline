from __future__ import annotations

from fastapi import FastAPI, HTTPException

from ecg.db import connect
from ecg.queries import get_recording, label_distribution, list_recordings
from ecg.signals import load_signal

app = FastAPI(
    title="ECG Pipeline API",
    description=(
        "Query interface over PTB-XL clinical ECG recordings. "
        "Engineering demonstration only — not a diagnostic tool."
    ),
    version="0.1.0",
)


@app.get("/")
def root():
    return {"name": "ECG Pipeline API", "docs": "/docs"}


@app.get("/recordings")
def get_recordings(limit: int = 50):
    """List recordings with features and diagnostic labels."""
    with connect() as conn:
        return list_recordings(conn, limit)


@app.get("/recordings/{ecg_id}")
def get_one(ecg_id: int):
    """Metadata, features, and labels for one recording."""
    with connect() as conn:
        record = get_recording(conn, ecg_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    return record


@app.get("/recordings/{ecg_id}/waveform")
def get_waveform(ecg_id: int, lead: int = 1, max_samples: int = 1000):
    """
    Waveform samples for one lead of a recording.

    Lead index 1 is lead II by convention.
    """
    with connect() as conn:
        record = get_recording(conn, ecg_id)
    if record is None:
        raise HTTPException(status_code=404, detail="Recording not found.")
    try:
        signal, meta = load_signal(record["filename_lr"])
    except Exception:  # noqa: BLE001 - signal file may not be downloaded
        raise HTTPException(
            status_code=404, detail="Signal file not available locally."
        ) from None

    samples = signal[:max_samples, lead].tolist()
    return {
        "ecg_id": ecg_id,
        "lead": lead,
        "sampling_rate": meta.get("fs"),
        "samples": samples,
    }


@app.get("/stats/labels")
def get_label_distribution():
    """Distribution of diagnostic superclasses across the dataset."""
    with connect() as conn:
        return label_distribution(conn)
