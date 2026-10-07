"""
Database configuration for GreenLens.
"""

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""


engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """
    Provide a database session for a request.
    """

    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()

def ensure_schema():
    """Add newly introduced nullable/metadata columns to existing SQLite DBs."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "inference_records" not in tables:
        return

    existing = {column["name"] for column in inspector.get_columns("inference_records")}
    additions = {
        "ideal_model": "VARCHAR(200)",
        "capability_gap": "FLOAT",
        "ideal_estimated_carbon_g": "FLOAT",
        "selected_estimated_carbon_g": "FLOAT",
        "fallback_used": "BOOLEAN DEFAULT 0",
        "selected_is_free": "BOOLEAN",
        "preset": "VARCHAR(20) DEFAULT 'balanced'",
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in existing:
                connection.execute(text(
                    f"ALTER TABLE inference_records ADD COLUMN {name} {sql_type}"
                ))
