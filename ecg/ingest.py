from __future__ import annotations

from pathlib import Path

import pandas as pd
import psycopg

from ecg.labels import load_superclass_map, parse_scp_codes, superclasses_for_record

DB_CSV = Path("data/ptbxl/ptbxl_database.csv")


def ingest_metadata(
    conn: psycopg.Connection,
    csv_path: Path = DB_CSV,
    max_records: int | None = None,
) -> int:
    """
    Load patients, recordings, and diagnostic labels from the PTB-XL CSV.

    Idempotent: re-running skips existing rows via ON CONFLICT.

    Returns:
        Number of recordings processed.
    """
    df = pd.read_csv(csv_path, index_col="ecg_id")
    if max_records is not None:
        df = df.head(max_records)

    superclass_map = load_superclass_map()

    patient_rows = []
    recording_rows = []
    label_rows = []

    for ecg_id, row in df.iterrows():
        patient_id = int(row["patient_id"])

        patient_rows.append(
            (
                patient_id,
                _int_or_none(row.get("age")),
                _int_or_none(row.get("sex")),
                _float_or_none(row.get("height")),
                _float_or_none(row.get("weight")),
            )
        )

        recording_rows.append(
            (
                int(ecg_id),
                patient_id,
                _str_or_none(row.get("recording_date")),
                _str_or_none(row.get("device")),
                _str_or_none(row.get("filename_lr")),
                _int_or_none(row.get("strat_fold")),
                _str_or_none(row.get("baseline_drift")),
                _str_or_none(row.get("static_noise")),
            )
        )

        codes = parse_scp_codes(row["scp_codes"])
        for superclass in superclasses_for_record(codes, superclass_map):
            label_rows.append((int(ecg_id), superclass))

    with conn.cursor() as cur:
        cur.executemany(
            "INSERT INTO patients (patient_id, age, sex, height, weight) "
            "VALUES (%s, %s, %s, %s, %s) ON CONFLICT (patient_id) DO NOTHING",
            patient_rows,
        )
        cur.executemany(
            "INSERT INTO recordings "
            "(ecg_id, patient_id, recording_date, device, filename_lr, "
            "strat_fold, baseline_drift, static_noise) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s) "
            "ON CONFLICT (ecg_id) DO NOTHING",
            recording_rows,
        )
        cur.executemany(
            "INSERT INTO diagnostic_labels (ecg_id, superclass) "
            "VALUES (%s, %s) ON CONFLICT (ecg_id, superclass) DO NOTHING",
            label_rows,
        )
    conn.commit()
    return len(recording_rows)


def _int_or_none(v):
    return int(v) if pd.notna(v) else None


def _float_or_none(v):
    return float(v) if pd.notna(v) else None


def _str_or_none(v):
    return str(v) if pd.notna(v) else None
