from __future__ import annotations

import numpy as np
from scipy import signal as sp_signal

SAMPLING_RATE = 100  # Hz, for the _lr (low-rate) records


def bandpass_filter(
    ecg: np.ndarray, low: float = 0.5, high: float = 40.0, fs: int = SAMPLING_RATE
) -> np.ndarray:
    """
    Bandpass-filter an ECG signal to remove baseline wander & high-freq noise.

    0.5 Hz removes slow baseline drift; 40 Hz removes muscle/electrical noise
    while preserving the QRS complex.
    """
    nyquist = fs / 2
    b, a = sp_signal.butter(2, [low / nyquist, high / nyquist], btype="band")
    return sp_signal.filtfilt(b, a, ecg)


def detect_r_peaks(ecg_lead: np.ndarray, fs: int = SAMPLING_RATE) -> np.ndarray:
    """
    Detect R-peak sample indices in a single ECG lead.

    Uses a simple, explainable approach: filter, then find peaks above a
    threshold w/ a minimum spacing (a refractory period).
    """
    filtered = bandpass_filter(ecg_lead, fs=fs)
    # Minimum spacing: no 2 beats closer than 0.3s (200 bpm ceiling).
    min_distance = int(0.3 * fs)
    # Threshold at a fraction of the signal's own scale.
    threshold = np.mean(filtered) + 0.5 * np.std(filtered)
    peaks, _ = sp_signal.find_peaks(filtered, height=threshold, distance=min_distance)
    return peaks
