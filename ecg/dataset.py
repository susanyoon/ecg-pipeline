from __future__ import annotations

import pandas as pd
import psycopg


def build_training_frame(conn: psycopg.Connection) -> pd.DataFrame:
    """
    Assemble a modeling table: features + demographics + binary NORM label.

    Joins signal_features to recordings, patients, and the label table.
    Only includes records that have extracted features.

    Returns:
        DataFrame with feature columns, `strat_fold`, and `is_normal` (0/1).
    """
    query = """
        SELECT
            f.ecg_id,
            f.heart_rate,
            f.mean_rr,
            f.rr_std,
            p.age,
            p.sex,
            r.strat_fold,
            CASE WHEN EXISTS(
                SELECT 1 FROM diagnostic_labels d
                WHERE d.ecg_id = f.ecg_id AND d.superclass = 'NORM'
            ) THEN 1 ELSE 0 END AS is_normal
        FROM signal_features f
        JOIN recordings r ON r.ecg_id = f.ecg_id
        JOIN patients p ON p.patient_id = r.patient_id
        WHERE f.heart_rate IS NOT NULL
    """
    with conn.cursor() as cur:
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]
    return pd.DataFrame(rows, columns=columns)
