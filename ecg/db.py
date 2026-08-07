from __future__ import annotations

import os

import psycopg
from dotenv import load_dotenv

load_dotenv()


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
