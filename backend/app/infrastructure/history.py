"""PostgreSQL persistence for anonymous generation history."""

import os

import psycopg
from psycopg.rows import dict_row
from psycopg.types.json import Jsonb


class HistoryRepository:
    def __init__(self, dsn: str):
        self.dsn = dsn

    def connect(self):
        return psycopg.connect(self.dsn, connect_timeout=5, row_factory=dict_row)

    def initialize(self):
        with self.connect() as connection:
            connection.execute("""CREATE TABLE IF NOT EXISTS generation_history (
                id uuid PRIMARY KEY, owner_hash text NOT NULL,
                created_at timestamptz NOT NULL DEFAULT now(), snapshot jsonb NOT NULL
            )""")
            connection.execute(
                "CREATE INDEX IF NOT EXISTS history_owner_date ON generation_history(owner_hash, created_at DESC)"
            )

    def list(self, owner: str):
        with self.connect() as connection:
            return connection.execute(
                "SELECT id, created_at, snapshot FROM generation_history WHERE owner_hash=%s ORDER BY created_at DESC LIMIT 30",
                (owner,),
            ).fetchall()

    def save(self, owner: str, identifier: str, snapshot: dict):
        with self.connect() as connection:
            # Serialize per-browser writes so concurrent requests cannot exceed retention.
            connection.execute("SELECT pg_advisory_xact_lock(hashtextextended(%s, 0))", (owner,))
            row = connection.execute(
                "INSERT INTO generation_history(id,owner_hash,snapshot) VALUES(%s,%s,%s) RETURNING id,created_at,snapshot",
                (identifier, owner, Jsonb(snapshot)),
            ).fetchone()
            connection.execute(
                "DELETE FROM generation_history WHERE owner_hash=%s AND id NOT IN (SELECT id FROM generation_history WHERE owner_hash=%s ORDER BY created_at DESC LIMIT 30)",
                (owner, owner),
            )
            return row

    def delete(self, owner: str, identifier: str) -> bool:
        with self.connect() as connection:
            result = connection.execute(
                "DELETE FROM generation_history WHERE id=%s AND owner_hash=%s", (identifier, owner)
            )
            return result.rowcount > 0


def create_history_repository():
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        return None
    repository = HistoryRepository(dsn)
    repository.initialize()
    return repository
