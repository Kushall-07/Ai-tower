from typing import List

from fastapi import APIRouter
from sqlmodel import Session, select

from ..data.data_os import get_logs_stats
from ..db.database import engine
from ..db.models import AgentRun

router = APIRouter()


@router.get("/recent", response_model=List[AgentRun])
def get_recent_runs(limit: int = 20):
    with Session(engine) as session:
        statement = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)
        results = session.exec(statement).all()
        return list(results)


@router.get("/analytics")
def get_logs_analytics():
    """
    Return high-level analytics for agent runs.
    Useful for dashboard summary cards.
    """
    stats = get_logs_stats()
    return stats
