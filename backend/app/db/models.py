from typing import Optional
from datetime import datetime

from sqlmodel import SQLModel, Field


class AgentRun(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    prompt: str
    response: str
    model: str

    trust_score: float
    risk_level: str

    policy_decision: str
    policy_risk_level: str

    risk_flags_json: str  # JSON-encoded list
    policy_reasons_json: str  # JSON-encoded list

    llm_error: Optional[str] = None


class Approval(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Link back to the agent run that triggered this approval
    agent_run_id: int = Field(index=True)

    # "pending" | "approved" | "rejected"
    status: str = Field(default="pending")

    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    decision_reason: Optional[str] = None


class Action(SQLModel, table=True):
    __tablename__ = "actions"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    agent_run_id: int = Field(foreign_key="agentrun.id")
    type: str  # e.g., "email_suggestion", "database_query", "api_call", etc.
    payload_json: str  # JSON string of the action details
    status: str = Field(default="pending")  # "pending", "simulated", "executed", "cancelled"
    executed_at: Optional[datetime] = None
    execution_result_json: Optional[str] = None  # Store results after execution