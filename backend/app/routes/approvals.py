from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from ..db.database import engine
from ..db.models import AgentRun, Approval

router = APIRouter()


class PendingApproval(BaseModel):
    approval_id: int
    run_id: int
    created_at: datetime
    prompt: str
    response_preview: str
    trust_score: float
    risk_level: str
    policy_decision: str


class ApprovalAction(BaseModel):
    reason: Optional[str] = None
    decided_by: Optional[str] = "human-reviewer"


@router.get("/pending", response_model=List[PendingApproval])
def get_pending_approvals(limit: int = 20):
    """
    Return pending approvals with basic info from the related AgentRun.
    """
    with Session(engine) as session:
        stmt = (
            select(Approval)
            .where(Approval.status == "pending")
            .order_by(Approval.created_at.desc())
            .limit(limit)
        )
        approvals = session.exec(stmt).all()

        results: List[PendingApproval] = []

        for ap in approvals:
            run = session.get(AgentRun, ap.agent_run_id)
            if not run:
                continue

            results.append(
                PendingApproval(
                    approval_id=ap.id,
                    run_id=run.id,
                    created_at=ap.created_at,
                    prompt=run.prompt,
                    response_preview=(run.response[:120] + "...")
                    if len(run.response) > 120
                    else run.response,
                    trust_score=run.trust_score,
                    risk_level=run.risk_level,
                    policy_decision=run.policy_decision,
                )
            )

        return results


@router.post("/{approval_id}/approve")
def approve(approval_id: int, action: ApprovalAction):
    with Session(engine) as session:
        ap = session.get(Approval, approval_id)
        if not ap:
            raise HTTPException(status_code=404, detail="Approval not found")

        if ap.status != "pending":
            raise HTTPException(status_code=400, detail="Approval already decided")

        ap.status = "approved"
        ap.decided_at = datetime.utcnow()
        ap.decided_by = action.decided_by
        ap.decision_reason = action.reason

        session.add(ap)
        session.commit()

        return {"status": "ok", "message": "Approval marked as approved."}


@router.post("/{approval_id}/reject")
def reject(approval_id: int, action: ApprovalAction):
    with Session(engine) as session:
        ap = session.get(Approval, approval_id)
        if not ap:
            raise HTTPException(status_code=404, detail="Approval not found")

        if ap.status != "pending":
            raise HTTPException(status_code=400, detail="Approval already decided")

        ap.status = "rejected"
        ap.decided_at = datetime.utcnow()
        ap.decided_by = action.decided_by
        ap.decision_reason = action.reason

        session.add(ap)
        session.commit()

        return {"status": "ok", "message": "Approval marked as rejected."}
