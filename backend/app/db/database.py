"""Database configuration for GreenLens."""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.core.config import settings


class Base(DeclarativeBase):
    """Base class for all database models."""


def _database_url() -> str:
    url = settings.DATABASE_URL
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    if url.startswith("postgresql://") and "+psycopg" not in url:
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


DATABASE_URL = _database_url()
_engine_options = {"pool_pre_ping": True}
if DATABASE_URL.startswith("sqlite"):
    _engine_options["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **_engine_options)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_schema():
    """Create missing tables and retain the legacy SQLite inference-column upgrade."""
    Base.metadata.create_all(bind=engine)
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    if "conversations" in tables:
        conversation_columns = {column["name"] for column in inspector.get_columns("conversations")}
        if "legacy_id" not in conversation_columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE conversations ADD COLUMN legacy_id VARCHAR(128)"))

    if "inference_records" not in tables:
        return

    existing = {column["name"] for column in inspector.get_columns("inference_records")}
    additions = {
        "user_id": ("UUID REFERENCES users(id) ON DELETE CASCADE" if engine.dialect.name == "postgresql" else "CHAR(32) REFERENCES users(id) ON DELETE CASCADE"),
        "ideal_model": "VARCHAR(200)",
        "capability_gap": "FLOAT",
        "ideal_estimated_carbon_g": "FLOAT",
        "selected_estimated_carbon_g": "FLOAT",
        "fallback_used": "BOOLEAN DEFAULT FALSE",
        "selected_is_free": "BOOLEAN",
        "preset": "VARCHAR(20) DEFAULT 'balanced'",
        "water_l": "FLOAT",
        "sustainability_source": "VARCHAR(40)",
    }
    with engine.begin() as connection:
        for name, sql_type in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE inference_records ADD COLUMN {name} {sql_type}"))
        connection.execute(text(
            "CREATE INDEX IF NOT EXISTS ix_inference_records_user_id "
            "ON inference_records (user_id)"
        ))
