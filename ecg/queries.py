from __future__ import annotations

import psycopg


def list_recordings(conn: psycopg.Connection, limit: int = 50) -> list[dict]:
    """
    Recordings that havve extracted features, with patient info & labels.
    """
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                r.ecg_id, p.age, p.sex, r.device, r.strat_fold,
                f.heart_rate, f.rr_std,
                ARRAY(
                    SELECT d.superclass FROM diagnostic_labels d
                    WHERE d.ecg_id = r.ecg_id ORDER BY d.superclass
                ) AS labels
            FROM recordings r
            JOIN patients p ON p.patient_id = r.patient_id
            JOIN signal_features f ON f.ecg_id = r.ecg_id
            ORDER BY r.ecg_id
            LIMIT %s
            """,
            (limit,),
        )
        columns = [d[0] for d in cur.description]
        return [dict(zip(columns, row, strict=True)) for row in cur.fetchall()]


def get_recording(conn: psycopg.Connection, ecg_id: int) -> dict | None:
    """One recording's metadata, features, and labels."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT
                r.ecg_id, r.filename_lr, r.device, r.recording_date,
                p.patient_id, p.age, p.sex,
                f.heart_rate, f.mean_rr, f.rr_std,
                ARRAY(
                    SELECT d.superclass FROM diagnostic_labels d
                    WHERE d.ecg_id = r.ecg_id ORDER BY d.superclass
                ) AS labels
            FROM recordings r
            JOIN patients p ON p.patient_id = r.patient_id
            LEFT JOIN signal_features f ON f.ecg_id = r.ecg_id
            WHERE r.ecg_id = %s
            """,
            (ecg_id,),
        )
        row = cur.fetchone()
        if row is None:
            return None
        columns = [d[0] for d in cur.description]
        return dict(zip(columns, row, strict=True))


def label_distribution(conn: psycopg.Connection) -> list[dict]:
    """Count of records per diagnostic superclass."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT superclass, COUNT(*) AS n FROM diagnostic_labels "
            "GROUP BY superclass ORDER BY n DESC"
        )
        return [{"superclass": s, "count": n} for s, n in cur.fetchall()]
