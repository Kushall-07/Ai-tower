from contextlib import contextmanager
from typing import Generator

from sqlmodel import SQLModel, Session, create_engine

# Path to your SQLite DB file (relative to backend/ directory)
DATABASE_URL = "sqlite:///data/control_tower.db"

# Create engine
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Import models and create tables if they don't exist.
    This is called on FastAPI startup.
    """
    # Important: import models so SQLModel sees all tables
    from app.db import models  # noqa: F401

    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """
    Dependency that FastAPI can use with Depends(get_session).
    Yields a database session tied to the global engine.
    """
    with Session(engine) as session:
        yield session
