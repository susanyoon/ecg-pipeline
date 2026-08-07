-- Patients: 1 row per patient (deduplicated from recrodings)
CREATE TABLE IF NOT EXISTS patients(
    patient_id  INTEGER PRIMARY KEY,
    age         INTEGER,
    sex         INTEGER,           -- PTB-XL encodes 0/1
    height      REAL,
    weight      REAL
);

-- Recordings: 1 row per ECG record
CREATE TABLE IF NOT EXISTS recordings (
    ecg_id           INTEGER PRIMARy KEY,
    patient_id       INTEGER NOT NULL REFERENCES patients(patient_id),
    recording_date   TIMESTAMP,
    device           TEXT,
    sampling_rate    INTEGER NOT NULL DEFAULT 100,
    filename_lr      TEXT NOT NULL,
    strat_fold       INTEGER,
    baseline_drift   TEXT,
    static_noise     TEXT
);

-- Diagnostic labels: 1 row per (record, superclass) = models multi-label
CREATE TABLE IF NOT EXISTS diagnostic_labels(
    id         BIGSERIAL PRIMARY KEY,
    ecg_id     INTEGER NOT NULL REFERENCES recordings(ecg_id),
    superclass TEXT NOT NULL,
    UNIQUE (ecg_id, superclass)
);

-- Signal features: extracted in Phase 3. 1 row per record
CREATE TABLE IF NOT EXISTS signal_features(
    ecg_id       INTEGER PRIMARY KEY REFERENCES recordings(ecg_id),
    heart_rate   REAL,
    mean_rr      REAL,
    rr_std       REAL,
    qrs_duration REAL
);

-- Indexes for the query patterns we will use
CREATE INDEX IF NOT EXISTS idx_labels_superclass
    ON diagnostic_labels (superclass);
CREATE INDEX IF NOT EXISTS idx_recordings_fold
    ON recordings (strat_fold);