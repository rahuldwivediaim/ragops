from sqlalchemy import text

from backend.database.session import SessionLocal


def main():
    db = SessionLocal()

    try:
        result = db.execute(text("SELECT version();"))
        print(result.scalar())
        print("\n✅ Database connection successful.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
