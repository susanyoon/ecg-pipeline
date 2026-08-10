from __future__ import annotations

import numpy as np

from ecg.processing import SAMPLING_RATE, detect_r_peaks


def extract_features(signal: np.ndarray, fs: int = SAMPLING_RATE) -> dict[str, float]:
    """
    Extract interpretable features from a 12-lead ECG.

    Uses lead II (index 1) for rhythm analysis - conventional for heart rate.

    Args:
        signal: array of shape (samples, 12).

    Returns:
        Dict of features; NaN-safe (returns None-like floats if undetectable).
    """
    lead_ii = signal[:, 1]
    peaks = detect_r_peaks(lead_ii, fs=fs)

    if len(peaks) < 2:
        # Not enough beats to compute intervals.
        return {
            "heart_rate": float("nan"),
            "mean_rr": float("nan"),
            "rr_std": float("nan"),
            "n_beats": float(len(peaks)),
        }

    rr_intervals = np.diff(peaks) / fs  # seconds b/w beats
    mean_rr = float(np.mean(rr_intervals))
    heart_rate = 60.0 / mean_rr  # beats per minute

    return {
        "heart_rate": heart_rate,
        "mean_rr": mean_rr,
        "rr_std": float(np.std(rr_intervals)),
        "n_beats": float(len(peaks)),
    }
