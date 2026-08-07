from __future__ import annotations

import typer
from rich.console import Console

from ecg.db import connect, init_schema
from ecg.ingest import ingest_metadata

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


if __name__ == "__main__":
    app()
