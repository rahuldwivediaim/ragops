from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from backend.database.config import get_database_settings

settings = get_database_settings()

engine = create_engine(
    settings.database_url,
    echo=settings.echo_sql,
    pool_size=settings.pool_size,
    max_overflow=settings.max_overflow,
    pool_timeout=settings.pool_timeout,
    pool_recycle=settings.pool_recycle,
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db():
    """
    Dependency for obtaining a database session.

    Ensures every session is properly closed.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
