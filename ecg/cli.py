from __future__ import annotations

import math

import typer
from rich.console import Console

from ecg.db import connect, init_schema
from ecg.download import download_signals
from ecg.features import extract_features
from ecg.ingest import ingest_metadata
from ecg.signals import load_signal

app = typer.Typer(help="ECG signal pipeline over PTB-XL.")
console = Console()


@app.callback()
def main():
    """
    ECG signal pipeline over PTB-XL.
    """
    pass


@app.command()
def initdb():
    """
    Create the database schema.
    """
    init_schema()
    console.print("[green]Schema created.[/green]")


@app.command()
def ingest(max_records: int = 2000):
    """
    Load PTB-XL metadata, labels, and patient records into the database.
    """
    with connect() as conn:
        count = ingest_metadata(conn, max_records=max_records)
    console.print(f"[green]Ingested {count} recordings.[/green]")


@app.command()
def fetch_signals(limit: int = 200):
    """Download WFDB signal files for the first N recordings in the DB."""
    with connect() as conn, conn.cursor() as cur:
        cur.execute(
            "SELECT filename_lr FROM recordings ORDER BY ecg_id LIMIT %s",
            (limit,),
        )
        paths = [row[0] for row in cur.fetchall()]
    download_signals(paths)
    console.print(f"[green]Downloaded {len(paths)} signal records.[/green]")


@app.command()
def extract(limit: int = 200):
    """Extract features from downloaded signals and store them."""
    with connect() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT ecg_id, filename_lr FROM recordings ORDER BY ecg_id LIMIT %s",
                (limit,),
            )
            records = cur.fetchall()

        processed = 0
        for ecg_id, filename_lr in records:
            try:
                sig, _ = load_signal(filename_lr)
            except Exception:
                continue  # signal not downloaded / unreadable; skip
            f = extract_features(sig)

            def clean(x):
                return None if math.isnan(x) else x

            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO signal_features "
                    "(ecg_id, heart_rate, mean_rr, rr_std) "
                    "VALUES (%s, %s, %s, %s) "
                    "ON CONFLICT (ecg_id) DO UPDATE SET "
                    "heart_rate = EXCLUDED.heart_rate, "
                    "mean_rr = EXCLUDED.mean_rr, rr_std = EXCLUDED.rr_std",
                    (
                        ecg_id,
                        clean(f["heart_rate"]),
                        clean(f["mean_rr"]),
                        clean(f["rr_std"]),
                    ),
                )
            conn.commit()
            processed += 1

    console.print(f"[green]Extracted features for {processed} records.[/green]")


if __name__ == "__main__":
    app()
