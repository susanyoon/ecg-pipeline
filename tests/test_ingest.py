from pathlib import Path

import pandas as pd

from ecg.db import connect, init_schema
from ecg.ingest import ingest_metadata


def _write_fixture_csv(tmp_path: Path) -> Path:
    df = pd.DataFrame(
        {
            "ecg_id": [1, 2],
            "patient_id": [100.0, 100.0],  # same patient, two recordings
            "age": [55, 55],
            "sex": [0, 0],
            "height": [None, None],
            "weight": [70.0, 70.0],
            "recording_date": ["2020-01-01", "2020-01-02"],
            "device": ["CS-12", "CS-12"],
            "filename_lr": ["records100/00000/00001_lr", "records100/00000/00002_lr"],
            "strat_fold": [1, 1],
            "baseline_drift": [None, None],
            "static_noise": [None, None],
            "scp_codes": ["{'NORM': 100.0}", "{'IMI': 100.0}"],
        }
    )
    p = tmp_path / "mini.csv"
    df.to_csv(p, index=False)
    return p


def _clear(conn):
    with conn.cursor() as cur:
        cur.execute("DELETE FROM diagnostic_labels")
        cur.execute("DELETE FROM signal_features")
        cur.execute("DELETE FROM recordings")
        cur.execute("DELETE FROM patients")
        conn.commit()


def test_ingest_loads_records_and_dedupes_patients(tmp_path, monkeypatch):
    # point the label map at the real scp_statements if present, else skip mapping
    import ecg.labels as labels

    monkeypatch.setattr(
        labels,
        "load_superclass_map",
        lambda *a, **k: {"NORM": "NORM", "IMI": "MI"},
    )
    import ecg.ingest as ingest_mod

    monkeypatch.setattr(
        ingest_mod, "load_superclass_map", lambda *a, **k: {"NORM": "NORM", "IMI": "MI"}
    )

    init_schema()
    with connect() as conn:
        _clear(conn)
        csv = _write_fixture_csv(tmp_path)
        count = ingest_metadata(conn, csv_path=csv)
        assert count == 2
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM patients")
            assert cur.fetchone()[0] == 1  # deduped to one patient
            cur.execute("SELECT COUNT(*) FROM recordings")
            assert cur.fetchone()[0] == 2
            cur.execute("SELECT COUNT(*) FROM diagnostic_labels")
            assert cur.fetchone()[0] == 2  # one NORM, one MI


def test_ingest_is_idempotent(tmp_path, monkeypatch):
    import ecg.ingest as ingest_mod

    monkeypatch.setattr(
        ingest_mod, "load_superclass_map", lambda *a, **k: {"NORM": "NORM", "IMI": "MI"}
    )
    init_schema()
    with connect() as conn:
        _clear(conn)
        csv = _write_fixture_csv(tmp_path)
        ingest_metadata(conn, csv_path=csv)
        ingest_metadata(conn, csv_path=csv)  # twice
        with conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM recordings")
            assert cur.fetchone()[0] == 2  # no duplicates
