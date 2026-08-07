from ecg.db import connect, init_schema


def test_schema_creates_all_tables():
    init_schema()
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public'"
        )
        tables = {row[0] for row in cur.fetchall()}
    for expected in ["patients", "recordings", "diagnostic_labels", "signal_features"]:
        assert expected in tables


def test_recording_requires_valid_patient():
    init_schema()
    with connect() as conn, conn.cursor() as cur:
        try:
            cur.execute(
                "INSERT INTO recordings (ecg_id, patient_id, filename_lr) "
                "VALUES (1, 999999, 'records100/00000/00001_lr')"
            )
            conn.commit()
            raise AssertionError("FK to patients was not enforced.")
        except Exception as e:
            conn.rollback()
            assert "foreign key" in str(e).lower() or "violates" in str(e).lower()


def test_labels_are_unique_per_record():
    init_schema()
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "INSERT INTO patients (patient_id) VALUES (1) ON CONFLICT DO NOTHING"
        )
        cur.execute(
            "INSERT INTO recordings (ecg_id, patient_id, filename_lr) "
            "VALUES (1, 1, 'x') ON CONFLICT DO NOTHING"
        )
        cur.execute(
            "INSERT INTO diagnostic_labels (ecg_id, superclass) "
            "VALUES (1, 'NORM') ON CONFLICT DO NOTHING"
        )
        conn.commit()
        # inserting the same (ecg_id, superclass) again must not duplicate
        cur.execute(
            "INSERT INTO diagnostic_labels (ecg_id, superclass) "
            "VALUES (1, 'NORM') ON CONFLICT DO NOTHING"
        )
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM diagnostic_labels WHERE ecg_id = 1")
        assert cur.fetchone()[0] == 1
