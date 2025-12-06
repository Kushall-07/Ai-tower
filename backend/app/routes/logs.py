from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import AgentRun

router = APIRouter(
    prefix="/logs",
    tags=["logs"],
)


class AgentRunLog(BaseModel):
    id: int
    created_at: str
    prompt: str
    response: str
    model: str
    trust_score: float
    risk_level: str
    policy_decision: str
    policy_risk_level: str

    @classmethod
    def from_model(cls, run: AgentRun) -> "AgentRunLog":
        return cls(
            id=run.id,
            created_at=run.created_at.isoformat() if run.created_at else "",
            prompt=run.prompt or "",
            response=run.response or "",
            model=run.model or "",
            trust_score=run.trust_score or 0.0,
            risk_level=run.risk_level or "unknown",
            policy_decision=run.policy_decision or "unknown",
            policy_risk_level=run.policy_risk_level or run.risk_level or "unknown",
        )


@router.get("/recent", response_model=List[AgentRunLog])
def recent_logs(
    limit: int = 50,
    session: Session = Depends(get_session),
):
    """
    Return most recent agent runs for dashboard logs.
    """
    statement = (
        select(AgentRun)
        .order_by(AgentRun.created_at.desc())
        .limit(limit)
    )
    runs = session.exec(statement).all()
    return [AgentRunLog.from_model(r) for r in runs]


@router.get("/analytics")
def logs_analytics(
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """
    Simple analytics for dashboard cards:
      - total_runs
      - by_risk_level
      - by_policy_decision
    """
    statement = select(AgentRun)
    runs = session.exec(statement).all()

    total = len(runs)
    by_risk_level: Dict[str, int] = {}
    by_policy_decision: Dict[str, int] = {}

    for r in runs:
        rl = (r.risk_level or "unknown").lower()
        by_risk_level[rl] = by_risk_level.get(rl, 0) + 1

        pd = (r.policy_decision or "unknown").lower()
        by_policy_decision[pd] = by_policy_decision.get(pd, 0) + 1

    return {
        "total_runs": total,
        "by_risk_level": by_risk_level,
        "by_policy_decision": by_policy_decision,
    }
