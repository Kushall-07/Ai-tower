import json
from fastapi import APIRouter
from sqlmodel import Session

from ..db.database import engine
from ..db.models import AgentRun, Approval
from ..llm.client import safe_generate
from ..trust.evaluator import evaluate_trust_and_risk
from ..policy.engine import evaluate_policies

router = APIRouter()


@router.post("/run")
def run_agent(data: dict):
    """
    Agent route with:
      - Secure LLM call
      - Trust & risk evaluation v1
      - Policy decision v1
    """
    prompt = data.get("prompt", "")

    # 1) Call secure LLM wrapper
    llm_result = safe_generate(prompt)
    llm_text = llm_result["text"]
    llm_error = llm_result["error"]
    llm_model = llm_result["model"]

    # 2) Trust & risk evaluation
    trust_info = evaluate_trust_and_risk(
        prompt=prompt,
        response=llm_text,
        llm_error=llm_error,
    )

    # 3) Policy evaluation (uses risk flags & patterns)
    policy_info = evaluate_policies(
        prompt=prompt,
        response=llm_text,
    )

    # 4) Persist audit log + create approval entry if needed
    with Session(engine) as session:
        run = AgentRun(
            prompt=prompt,
            response=llm_text,
            model=llm_model,
            trust_score=trust_info["trust_score"],
            risk_level=trust_info["risk_level"],
            policy_decision=policy_info["decision"],
            policy_risk_level=policy_info["risk_level"],
            risk_flags_json=json.dumps(trust_info["risk_flags"]),
            policy_reasons_json=json.dumps(policy_info["reasons"]),
            llm_error=llm_error,
        )
        session.add(run)
        session.flush()  # assigns run.id

        # If policy says "needs_approval", create a pending Approval
        if policy_info["decision"] == "needs_approval":
            approval = Approval(
                agent_run_id=run.id,
                status="pending",
            )
            session.add(approval)

        session.commit()

    return {
        "status": "ok",
        "message": "Agent runner live!",
        "prompt_sent": prompt,
        "response": llm_text,
        "model": llm_model,
        # Trust layer
        "trust_score": trust_info["trust_score"],
        "risk_level": trust_info["risk_level"],
        "risk_flags": trust_info["risk_flags"],
        "explainability": trust_info["explanation"],
        # Policy layer
        "policy_decision": policy_info["decision"],
        "policy_reasons": policy_info["reasons"],
        "policy_risk_level": policy_info["risk_level"],
        "policy_risk_flags": policy_info["risk_flags"],
    }
