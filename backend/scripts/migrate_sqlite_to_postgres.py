"""Idempotently copy existing GreenLens inference records from SQLite to PostgreSQL.

Run from the backend directory after setting DATABASE_URL in .env:
    python scripts/migrate_sqlite_to_postgres.py --source ./greenlens.db
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import text
from app.db.database import Base, SessionLocal, engine
from app.db import models  # noqa: F401 - register all mapped tables
from app.db.models import InferenceRecord


def parse_datetime(value):
    if not value:
        return datetime.utcnow()
    if isinstance(value, datetime):
        return value
    return datetime.fromisoformat(str(value).replace("Z", "+00:00"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", default="./greenlens.db", help="Path to the existing SQLite database")
    parser.add_argument("--dry-run", action="store_true", help="Count records without inserting them")
    args = parser.parse_args()

    source_path = Path(args.source).resolve()
    if not source_path.exists():
        raise SystemExit(f"SQLite source database not found: {source_path}")

    Base.metadata.create_all(bind=engine)
    source = sqlite3.connect(str(source_path))
    source.row_factory = sqlite3.Row
    try:
        table = source.execute(
            "SELECT name FROM sqlite_master WHERE type='table' AND name='inference_records'"
        ).fetchone()
        if not table:
            raise SystemExit("The SQLite database has no inference_records table.")

        rows = source.execute("SELECT * FROM inference_records ORDER BY id").fetchall()
        db = SessionLocal()
        try:
            existing_ids = {
                item[0] for item in db.query(InferenceRecord.id).all()
            }
            pending = []
            for row in rows:
                if row["id"] in existing_ids:
                    continue
                data = dict(row)
                data["created_at"] = parse_datetime(data.get("created_at"))
                for boolean_field in ("fallback_used", "selected_is_free", "success"):
                    if data.get(boolean_field) is not None:
                        data[boolean_field] = bool(data[boolean_field])
                allowed = {
                    "id", "prompt", "provider", "model", "ideal_model", "capability_gap",
                    "ideal_estimated_carbon_g", "selected_estimated_carbon_g", "fallback_used",
                    "selected_is_free", "preset", "task_type", "recommendation_score",
                    "latency_ms", "prompt_tokens", "completion_tokens", "total_tokens",
                    "energy_wh", "carbon_g", "green_score", "success", "created_at",
                }
                pending.append(InferenceRecord(**{key: value for key, value in data.items() if key in allowed}))
            if args.dry_run:
                print(f"Source records: {len(rows)}; records to import: {len(pending)} (dry run)")
                return
            db.add_all(pending)
            db.commit()
            if engine.dialect.name == "postgresql":
                db.execute(text(
                    "SELECT setval(pg_get_serial_sequence('inference_records', 'id'), "
                    "COALESCE((SELECT MAX(id) FROM inference_records), 1), true)"
                ))
                db.commit()
            print(f"Imported {len(pending)} inference records. Existing records were left unchanged.")
        finally:
            db.close()
    finally:
        source.close()


if __name__ == "__main__":
    main()
