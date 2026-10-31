"""Database engine, session management, and Base declarative."""

import logging
from collections.abc import Iterator
from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from .config import settings

logger = logging.getLogger("bounty_hunters.db")

# Detect SQLite for testing vs PostgreSQL for production
db_url_str = str(settings.database_url)
is_sqlite = db_url_str.startswith("sqlite")

engine_kwargs = {"pool_pre_ping": True}
if not is_sqlite:
    engine_kwargs.update({
        "pool_size": 5,
        "max_overflow": 5,
    })

engine = create_engine(settings.database_url, **engine_kwargs)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


class Base(DeclarativeBase):
    pass


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a database session and safely closes it."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ping_db() -> bool:
    """Test database connectivity."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as exc:
        logger.warning("Database ping failed: %s", exc)
        return False


def init_db() -> None:
    """Create all tables in the database if they don't exist."""
    from . import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
