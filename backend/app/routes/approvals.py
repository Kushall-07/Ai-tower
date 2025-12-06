from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.database import get_session
from app.db.models import Approval, AgentRun

router = APIRouter(prefix="/approvals", tags=["approvals"])


class ApprovalResponse(BaseModel):
    id: int
    created_at: datetime
    updated_at: Optional[datetime]
    agent_run_id: int
    status: str
    risk_level: Optional[str] = None
    policy_decision: Optional[str] = None
    reviewer: Optional[str] = None
    notes: Optional[str] = None
    prompt: Optional[str] = None

    @classmethod
    def from_model(cls, approval: Approval, prompt: Optional[str] = None):
        return cls(
            id=approval.id,
            created_at=approval.created_at,
            updated_at=getattr(approval, "updated_at", None),
            agent_run_id=approval.agent_run_id,
            status=approval.status,
            risk_level=getattr(approval, "risk_level", None),
            policy_decision=getattr(approval, "policy_decision", None),
            reviewer=getattr(approval, "reviewer", None),
            notes=getattr(approval, "notes", None),
            prompt=prompt,
        )


class ApprovalUpdateRequest(BaseModel):
    reviewer: Optional[str] = None
    notes: Optional[str] = None


@router.get("/pending", response_model=List[ApprovalResponse])
def get_pending_approvals(
    session: Session = Depends(get_session),
    limit: int = 100,
):
    """
    List approvals that are currently pending.
    """
    stmt = (
        select(Approval)
        .where(Approval.status == "pending")
        .order_by(Approval.created_at.desc())
        .limit(limit)
    )
    approvals = session.exec(stmt).all()

    # join with AgentRun to get prompt
    responses: List[ApprovalResponse] = []
    for a in approvals:
        run = session.get(AgentRun, a.agent_run_id)
        responses.append(
            ApprovalResponse.from_model(a, prompt=run.prompt if run else None)
        )

    return responses


@router.get("/all", response_model=List[ApprovalResponse])
def get_all_approvals(
    status: Optional[str] = None,
    limit: int = 200,
    session: Session = Depends(get_session),
):
    """
    List approvals, optionally filtered by status.
    """
    stmt = select(Approval)

    if status:
        stmt = stmt.where(Approval.status == status)

    stmt = stmt.order_by(Approval.created_at.desc()).limit(limit)
    approvals = session.exec(stmt).all()

    responses: List[ApprovalResponse] = []
    for a in approvals:
        run = session.get(AgentRun, a.agent_run_id)
        responses.append(
            ApprovalResponse.from_model(a, prompt=run.prompt if run else None)
        )

    return responses


def _get_approval_or_404(approval_id: int, session: Session) -> Approval:
    approval = session.get(Approval, approval_id)
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval


@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
def approve(
    approval_id: int,
    payload: ApprovalUpdateRequest,
    session: Session = Depends(get_session),
):
    """
    Mark an approval as approved.
    """
    approval = _get_approval_or_404(approval_id, session)

    approval.status = "approved"
    if hasattr(approval, "updated_at"):
        approval.updated_at = datetime.utcnow()
    if payload.reviewer is not None and hasattr(approval, "reviewer"):
        approval.reviewer = payload.reviewer
    if payload.notes is not None and hasattr(approval, "notes"):
        approval.notes = payload.notes

    session.add(approval)
    session.commit()
    session.refresh(approval)

    run = session.get(AgentRun, approval.agent_run_id)
    return ApprovalResponse.from_model(approval, prompt=run.prompt if run else None)


@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
def reject(
    approval_id: int,
    payload: ApprovalUpdateRequest,
    session: Session = Depends(get_session),
):
    """
    Mark an approval as rejected.
    """
    approval = _get_approval_or_404(approval_id, session)

    approval.status = "rejected"
    if hasattr(approval, "updated_at"):
        approval.updated_at = datetime.utcnow()
    if payload.reviewer is not None and hasattr(approval, "reviewer"):
        approval.reviewer = payload.reviewer
    if payload.notes is not None and hasattr(approval, "notes"):
        approval.notes = payload.notes

    session.add(approval)
    session.commit()
    session.refresh(approval)

    run = session.get(AgentRun, approval.agent_run_id)
    return ApprovalResponse.from_model(approval, prompt=run.prompt if run else None)
