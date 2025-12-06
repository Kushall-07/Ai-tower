from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import json
from sqlmodel import Session

from app.db.database import get_session
from app.db.models import AgentRun, Approval, Action
from app.llm.client import safe_generate
from app.trust.evaluator import evaluate_trust_and_risk

router = APIRouter(
    prefix="/agent",
    tags=["agent"],
)


class AgentRequest(BaseModel):
    prompt: str


class AgentResponse(BaseModel):
    status: str
    message: str
    prompt_sent: str
    response: Optional[str]
    model: Optional[str]
    trust_score: float
    risk_level: str
    risk_flags: List[str]
    policy_decision: str
    policy_reasons: List[str]
    policy_risk_level: str
    policy_risk_flags: List[str]
    explainability: str


@router.post("/run", response_model=AgentResponse)
def run_agent(req: AgentRequest, session: Session = Depends(get_session)):
    """
    Main agent entrypoint:
      1) Call LLM via safe_generate
      2) Evaluate trust & risk
      3) Apply simple policy logic
      4) Store AgentRun (+ Approval if needed)
    """
    prompt = req.prompt.strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt cannot be empty")

    # 1) Call LLM
    llm_result = safe_generate(prompt)
    llm_text = llm_result.get("text")
    llm_error = llm_result.get("error")
    model_name = llm_result.get("model", "unknown")
    suggested_actions = llm_result.get("actions", []) or []

    # 2) Evaluate trust & risk
    tr = evaluate_trust_and_risk(prompt, llm_text, llm_error)
    trust_score: float = tr["trust_score"]
    risk_level: str = tr["risk_level"]
    risk_flags: list[str] = tr["risk_flags"]
    explainability: str = tr["explanation"]

    # 3) Very simple policy logic (inline)
    policy_decision = "allow"
    policy_reasons: list[str] = []
    policy_risk_level = risk_level
    policy_risk_flags = risk_flags.copy()

    flags_set = set(risk_flags)

    if "destructive_actions" in flags_set:
        policy_decision = "block"
        policy_reasons.append(
            "Prompt/response appears to contain destructive actions, policy blocks such requests."
        )
    elif "security_sensitive" in flags_set or risk_level == "high":
        policy_decision = "needs_approval"
        policy_reasons.append(
            "Prompt/response appears security-sensitive or high-risk, requires human approval."
        )
    elif "privacy_sensitive" in flags_set or "financial_sensitive" in flags_set:
        policy_decision = "needs_approval"
        policy_reasons.append(
            "Prompt/response touches sensitive personal or financial data, requires human approval."
        )
    else:
        policy_decision = "allow"
        policy_reasons.append(
            "No high-risk patterns detected, allowed by default policy."
        )

    # 4) Store AgentRun
    run = AgentRun(
        prompt=prompt,
        response=llm_text or "",
        model=model_name,
        trust_score=trust_score,
        risk_level=risk_level,
        policy_decision=policy_decision,
        policy_risk_level=policy_risk_level,
        risk_flags_json=json.dumps(risk_flags),
        policy_reasons_json=json.dumps(policy_reasons),
        llm_error=llm_error,
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    # 5) If risky or blocked, create an Approval entry
    needs_approval = (
        risk_level in ("medium", "high") or policy_decision in ("block", "needs_approval")
    )

    if needs_approval:
        approval = Approval(
            agent_run_id=run.id,
            status="pending",
        )
        session.add(approval)
        session.commit()

    # 6) Store any suggested actions from the LLM
    #    These are "pending" by default so a human / policy layer can approve or simulate.
    for act in suggested_actions:
        if not isinstance(act, dict):
            continue
        a_type = act.get("type") or "other"
        payload = act.get("payload") or {}
        if not isinstance(payload, dict):
            payload = {}

        action = Action(
            agent_run_id=run.id,
            type=a_type,
            payload_json=json.dumps(payload),
            status="pending",  # can be 'pending' until sandbox / approval
        )
        session.add(action)

    if suggested_actions:
        session.commit()

    # 7) Build response
    return AgentResponse(
        status="ok",
        message="Agent runner live!",
        prompt_sent=prompt,
        response=llm_text,
        model=model_name,
        trust_score=trust_score,
        risk_level=risk_level,
        risk_flags=risk_flags,
        policy_decision=policy_decision,
        policy_reasons=policy_reasons,
        policy_risk_level=policy_risk_level,
        policy_risk_flags=policy_risk_flags,
        explainability=explainability,
    )
