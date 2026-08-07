from __future__ import annotations

import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

load_dotenv()

SCHEMA_PATH = Path(__file__).parent / "schema.sql"


def init_schema(conn: psycopg.Connection | None = None) -> None:
    """
    Create tables & indexes from schema.sql (idempotent).
    """
    sql = SCHEMA_PATH.read_text()
    own = conn is None
    if own:
        conn = connect()
    try:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()
    finally:
        if own:
            conn.close()


def get_connection_string() -> str:
    """
    Read the database URL from the environment.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise RuntimeError(
            "DATABASE_URL is not set. Copy .env.example to .env or export it."
        )
    return url


def connect() -> psycopg.Connection:
    """
    Open a new connection to the database.
    """
    return psycopg.connect(get_connection_string())


def ping() -> bool:
    """
    Return True if the database is reachable.
    """
    with connect() as conn, conn.cursor() as cur:
        cur.execute("SELECT 1")
        return cur.fetchone() == (1,)
