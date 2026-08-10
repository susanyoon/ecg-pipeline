from __future__ import annotations

from pathlib import Path

import numpy as np
import wfdb

DATA_ROOT = Path("data/ptbxl")


def load_signal(filename_lr: str) -> tuple[np.ndarray, dict]:
    """
    Load 1 ECG record's waveform via WFDB.

    Args:
        filename_lr: The record path from the metadata (no extension),
            e.g. "records100/00000/00001_lr".

    Returns:
        (signal, meta) where signal is shape (samples, 12) - 12 leads -
        and meta is the WFDB header info dict.
    """
    record_path = str(DATA_ROOT / filename_lr)
    signal, meta = wfdb.rdsamp(record_path)
    return signal, meta
