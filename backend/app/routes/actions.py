from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import json

from app.db.database import get_session
from app.db.models import Action, AgentRun, Approval

router = APIRouter(prefix="/actions", tags=["actions"])


class ActionSimulateRequest(BaseModel):
    agent_run_id: int
    type: str
    payload: dict


class ActionResponse(BaseModel):
    id: int
    created_at: datetime
    agent_run_id: int
    type: str
    payload: dict
    status: str
    executed_at: Optional[datetime] = None
    execution_result: Optional[dict] = None

    @classmethod
    def from_action(cls, action: Action):
        return cls(
            id=action.id,
            created_at=action.created_at,
            agent_run_id=action.agent_run_id,
            type=action.type,
            payload=json.loads(action.payload_json),
            status=action.status,
            executed_at=action.executed_at,
            execution_result=json.loads(action.execution_result_json)
            if action.execution_result_json
            else None,
        )


@router.post("/simulate", response_model=ActionResponse)
def simulate_action(
    request: ActionSimulateRequest,
    session: Session = Depends(get_session),
):
    """
    Simulate an action without executing it.
    Stores the action with status='simulated' or 'pending' for risky types.
    """
    agent_run = session.get(AgentRun, request.agent_run_id)
    if not agent_run:
        raise HTTPException(status_code=404, detail="AgentRun not found")

    risky_types = ["database_mutation", "email_send", "api_call_external", "file_delete"]
    status = "pending" if request.type in risky_types else "simulated"

    action = Action(
        agent_run_id=request.agent_run_id,
        type=request.type,
        payload_json=json.dumps(request.payload),
        status=status,
    )

    session.add(action)
    session.commit()
    session.refresh(action)

    return ActionResponse.from_action(action)


@router.get("/by-run/{agent_run_id}", response_model=List[ActionResponse])
def get_actions_by_run(
    agent_run_id: int,
    session: Session = Depends(get_session),
):
    """
    Get all actions associated with a given AgentRun.
    """
    statement = (
        select(Action)
        .where(Action.agent_run_id == agent_run_id)
        .order_by(Action.created_at.desc())
    )
    actions = session.exec(statement).all()
    return [ActionResponse.from_action(a) for a in actions]


@router.get("/all", response_model=List[ActionResponse])
def get_all_actions(
    status: Optional[str] = None,
    limit: int = 100,
    session: Session = Depends(get_session),
):
    """
    Get all actions, optionally filtered by status.
    """
    statement = select(Action)

    if status:
        statement = statement.where(Action.status == status)

    statement = statement.order_by(Action.created_at.desc()).limit(limit)
    actions = session.exec(statement).all()
    return [ActionResponse.from_action(a) for a in actions]


@router.post("/{action_id}/execute", response_model=ActionResponse)
def execute_action(
    action_id: int,
    session: Session = Depends(get_session),
):
    """
    Execute a simulated action (placeholder:
    we only mark as executed with a mock result).
    """
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if action.status == "executed":
        raise HTTPException(status_code=400, detail="Action already executed")

    if action.status == "cancelled":
        raise HTTPException(status_code=400, detail="Action is cancelled")

    # Check approvals for this agent run
    stmt = (
        select(Approval)
        .where(Approval.agent_run_id == action.agent_run_id)
        .order_by(Approval.created_at.desc())
    )
    approval = session.exec(stmt).first()

    if approval and approval.status != "approved":
        # approval exists but is not yet approved
        raise HTTPException(
            status_code=403,
            detail="Action requires approval before execution",
        )

    result = {
        "success": True,
        "message": f"Action {action.type} simulated successfully",
        "simulated": True,
    }

    action.status = "executed"
    action.executed_at = datetime.utcnow()
    action.execution_result_json = json.dumps(result)

    session.add(action)
    session.commit()
    session.refresh(action)

    return ActionResponse.from_action(action)


@router.post("/{action_id}/cancel", response_model=ActionResponse)
def cancel_action(
    action_id: int,
    session: Session = Depends(get_session),
):
    """
    Cancel a pending or simulated action.
    """
    action = session.get(Action, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")

    if action.status == "executed":
        raise HTTPException(status_code=400, detail="Cannot cancel executed action")

    action.status = "cancelled"

    session.add(action)
    session.commit()
    session.refresh(action)

    return ActionResponse.from_action(action)
