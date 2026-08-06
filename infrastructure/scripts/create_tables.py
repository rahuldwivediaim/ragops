"""
Development utility only.

Do not use for schema management.
Use Alembic migrations instead.
"""

from backend.database import Base, engine

# Import every model so SQLAlchemy registers them.


def main() -> None:
    Base.metadata.create_all(bind=engine)
    print("✅ All database tables created successfully.")


if __name__ == "__main__":
    main()
