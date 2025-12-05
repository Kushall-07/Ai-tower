from sqlmodel import SQLModel, create_engine
from pathlib import Path

# Store DB in backend/data/control_tower.db
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
DATA_DIR.mkdir(exist_ok=True)
DATABASE_URL = f"sqlite:///{DATA_DIR / 'control_tower.db'}"

engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """
    Create all tables if they don't exist.
    Called on app startup.
    """
    SQLModel.metadata.create_all(engine)
