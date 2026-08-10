import numpy as np

from ecg.processing import bandpass_filter, detect_r_peaks


def test_bandpass_removes_baseline_drift():
    fs = 100
    t = np.linspace(0, 10, 10 * fs)
    # a slow 0.1 Hz drift plus a fast 10 Hz component
    drift = np.sin(2 * np.pi * 0.1 * t)
    beat = np.sin(2 * np.pi * 10 * t)
    filtered = bandpass_filter(drift + beat, fs=fs)
    # the drift should be largely removed -> filtered std closer to the beat alone
    assert np.std(filtered) < np.std(drift + beat)


def test_detect_r_peaks_on_synthetic_beats():
    fs = 100
    # simulate 10 evenly spaced spikes (1 per second -> 60 bpm)
    sig = np.zeros(10 * fs)
    for i in range(10):
        sig[i * fs] = 5.0  # a spike each second
    peaks = detect_r_peaks(sig, fs=fs)
    # should find roughly 10 beats
    assert 8 <= len(peaks) <= 10
