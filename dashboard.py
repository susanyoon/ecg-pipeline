"""
Clinical-facing view over the ECG pipeline.

Engineering demonstration only — not a diagnostic tool.
"""

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from ecg.db import connect
from ecg.processing import bandpass_filter
from ecg.queries import get_recording, label_distribution, list_recordings
from ecg.signals import load_signal

st.set_page_config(page_title="ECG Pipeline", layout="wide")

st.title("ECG Signal Pipeline")
st.caption("Engineering demonstration over the PTB-XL dataset — not a diagnostic tool.")


@st.cache_data
def load_recordings():
    with connect() as conn:
        return pd.DataFrame(list_recordings(conn, limit=500))


@st.cache_data
def load_labels():
    with connect() as conn:
        return pd.DataFrame(label_distribution(conn))


recordings = load_recordings()

if recordings.empty:
    st.warning("No records with extracted features. Run `ecg extract` first.")
    st.stop()

# --- Sidebar: pick a record ---
st.sidebar.header("Select a recording")
ecg_id = st.sidebar.selectbox("ECG ID", recordings["ecg_id"].tolist())
show_filtered = st.sidebar.checkbox("Show filtered signal", value=True)

# --- Record detail ---
with connect() as conn:
    record = get_recording(conn, int(ecg_id))

col1, col2, col3, col4 = st.columns(4)
col1.metric("Age", record["age"] if record["age"] else "—")
col2.metric(
    "Heart rate", f"{record['heart_rate']:.0f} bpm" if record["heart_rate"] else "—"
)
col3.metric("HRV (RR std)", f"{record['rr_std']:.3f}" if record["rr_std"] else "—")
col4.metric("Labels", ", ".join(record["labels"]) if record["labels"] else "—")

# --- Waveform ---
st.subheader("Lead II waveform")
try:
    signal, meta = load_signal(record["filename_lr"])
    lead_ii = signal[:, 1]
    fig, ax = plt.subplots(figsize=(12, 3))
    ax.plot(lead_ii, linewidth=0.8, label="Raw", alpha=0.6)
    if show_filtered:
        ax.plot(bandpass_filter(lead_ii), linewidth=0.8, label="Filtered")
    ax.set_xlabel("Sample")
    ax.set_ylabel("mV")
    ax.legend()
    ax.grid(alpha=0.3)
    st.pyplot(fig)
except Exception as e:  # noqa: BLE001 - signal may not be downloaded
    st.info(f"Signal file not available locally for this record. ({e})")

# --- Dataset overview ---
st.subheader("Dataset overview")
left, right = st.columns(2)

with left:
    st.write("**Diagnostic superclass distribution**")
    st.dataframe(load_labels(), hide_index=True)

with right:
    st.write("**Heart rate distribution**")
    hr = recordings["heart_rate"].dropna()
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ax2.hist(hr, bins=30)
    ax2.set_xlabel("Heart rate (bpm)")
    ax2.set_ylabel("Records")
    st.pyplot(fig2)
