from __future__ import annotations

import typer
from rich.console import Console

from ecg.db import init_schema

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


if __name__ == "__main__":
    app()
