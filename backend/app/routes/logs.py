from typing import List

from fastapi import APIRouter
from sqlmodel import Session, select

from ..db.database import engine
from ..db.models import AgentRun

router = APIRouter()


@router.get("/recent", response_model=List[AgentRun])
def get_recent_runs(limit: int = 20):
    with Session(engine) as session:
        statement = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)
        results = session.exec(statement).all()
        return list(results)
