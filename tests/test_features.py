import numpy as np

from ecg.features import extract_features


def test_heart_rate_from_regular_beats():
    fs = 100
    # 12-lead array; put spikes at 1 Hz in lead II (index 1) -> 60 bpm
    sig = np.zeros((10 * fs, 12))
    for i in range(10):
        sig[i * fs, 1] = 5.0
    features = extract_features(sig, fs=fs)
    # 1 beat per second -> ~60 bpm
    assert 55 <= features["heart_rate"] <= 65


def test_features_handle_flat_signal():
    fs = 100
    sig = np.zeros((10 * fs, 12))  # no beats
    features = extract_features(sig, fs=fs)
    assert np.isnan(features["heart_rate"])  # gracefully returns NaN
