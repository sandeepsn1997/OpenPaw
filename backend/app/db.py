"""Database utilities and session management."""

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .database import Base

# Default SQLite database
DATABASE_URL = "sqlite:///./openpaw_v2.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db():
    """Initialize database tables and migrate schema if needed."""
    Base.metadata.create_all(bind=engine)
    _migrate_tasks_table()


def _migrate_tasks_table():
    """Add missing columns to the tasks table if they don't exist."""
    import sqlite3

    db_path = DATABASE_URL.replace("sqlite:///./", "")
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(tasks)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        migrations = [
            ("task_type", 'TEXT DEFAULT "one_time"'),
            ("scheduled_time", "TEXT"),
            ("scheduled_date", "TEXT"),
            ("recurrence", 'TEXT DEFAULT "one_time"'),
            ("next_run_at", "DATETIME"),
        ]

        for col_name, col_def in migrations:
            if col_name not in existing_cols:
                cursor.execute(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_def}")

        conn.commit()
        conn.close()
    except Exception:
        pass  # Table might not exist yet, create_all will handle it


def get_db() -> Session:
    """Get database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
