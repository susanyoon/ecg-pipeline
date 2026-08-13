from __future__ import annotations

import math

import typer
from rich.console import Console

from ecg.charts import plot_confusion_matrix
from ecg.dataset import build_training_frame
from ecg.db import connect, init_schema
from ecg.download import download_signals
from ecg.features import extract_features
from ecg.ingest import ingest_metadata
from ecg.model import evaluate, prepare_xy, split_by_fold, train_model
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


@app.command()
def train(chart: str = "charts/confusion_matrix.png"):
    """Train the baseline classifier and report honest evaluation metrics."""
    with connect() as conn:
        df = build_training_frame(conn)

    console.print(f"Records with features: {len(df)}")
    console.print(
        f"Normal: {int(df['is_normal'].sum())}, "
        f"Abnormal: {int((1 - df['is_normal']).sum())}"
    )

    train_df, test_df = split_by_fold(df)
    if len(test_df) == 0:
        console.print(
            "[yellow]No records in the test fold — ingest more data.[/yellow]"
        )
        raise typer.Exit(code=1)

    X_train, y_train = prepare_xy(train_df)
    X_test, y_test = prepare_xy(test_df)

    console.print(f"Train: {len(X_train)}, Test: {len(X_test)}")

    model = train_model(X_train, y_train)
    results = evaluate(model, X_test, y_test)

    console.print("\n[bold]Classification report:[/bold]")
    console.print(results["report_text"])
    console.print(f"ROC AUC: {results['roc_auc']:.3f}")

    plot_confusion_matrix(results["confusion_matrix"], chart)
    console.print(f"[green]Confusion matrix saved to {chart}[/green]")


if __name__ == "__main__":
    app()
