import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "skilloutcome.db"
DEFAULT_DATABASE_URL = f"sqlite:///{DEFAULT_DATABASE_PATH.as_posix()}"


class Settings:
    """Application settings loaded from environment variables."""

    DATABASE_URL: str = os.getenv("DATABASE_URL", DEFAULT_DATABASE_URL)
    @property
    def is_sqlite(self) -> bool:
        return self.DATABASE_URL.startswith("sqlite")
    @property
    def is_postgres(self) -> bool:
        return self.DATABASE_URL.startswith(("postgresql://", "postgresql+psycopg2://"))
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-do-not-use-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    # The ML API is an independently deployed service.  Keep each timeout
    # explicit so slow model inference cannot consume backend connections
    # indefinitely.
    ML_SERVICE_URL: str = os.getenv("ML_SERVICE_URL", "http://127.0.0.1:8001").rstrip("/")
    ML_CONNECT_TIMEOUT_SECONDS: float = float(
        os.getenv("ML_CONNECT_TIMEOUT_SECONDS", "2")
    )
    ML_READ_TIMEOUT_SECONDS: float = float(
        os.getenv("ML_READ_TIMEOUT_SECONDS", "10")
    )
    ML_WRITE_TIMEOUT_SECONDS: float = float(
        os.getenv("ML_WRITE_TIMEOUT_SECONDS", "10")
    )
    ML_POOL_TIMEOUT_SECONDS: float = float(
        os.getenv("ML_POOL_TIMEOUT_SECONDS", "2")
    )


settings = Settings()
