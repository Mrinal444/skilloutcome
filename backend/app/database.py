from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings

# SQLite requires check_same_thread=False for FastAPI's async context
connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args["check_same_thread"] = False

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def ensure_development_schema():
    """Add nullable ownership columns to existing SQLite development databases."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    with engine.begin() as connection:
        tables = {
            row[1] for row in connection.execute(text("PRAGMA table_info(employers)"))
        }
        if "user_id" not in tables:
            connection.execute(text("ALTER TABLE employers ADD COLUMN user_id INTEGER"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_employers_user_id ON employers (user_id)"))
        tables = {
            row[1] for row in connection.execute(text("PRAGMA table_info(training_programs)"))
        }
        if "provider_user_id" not in tables:
            connection.execute(text("ALTER TABLE training_programs ADD COLUMN provider_user_id INTEGER"))
            connection.execute(text("CREATE INDEX IF NOT EXISTS ix_training_programs_provider_user_id ON training_programs (provider_user_id)"))


def initialize_database():
    """Create or minimally upgrade only the local SQLite fallback database."""
    if settings.is_sqlite:
        Base.metadata.create_all(bind=engine)
        ensure_development_schema()


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
