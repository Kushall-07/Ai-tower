from fastapi import APIRouter

from ..llm.client import safe_generate
from ..trust.evaluator import evaluate_trust_and_risk

router = APIRouter()


@router.post("/run")
def run_agent(data: dict):
    """
    Day-2 Agent route with Trust & Risk evaluation v1.
    """
    prompt = data.get("prompt", "")

    # 1) Call secure LLM wrapper
    llm_result = safe_generate(prompt)
    llm_text = llm_result["text"]
    llm_error = llm_result["error"]
    llm_model = llm_result["model"]

    # 2) Evaluate trust and risk
    trust_info = evaluate_trust_and_risk(
        prompt=prompt,
        response=llm_text,
        llm_error=llm_error,
    )

    return {
        "status": "ok",
        "message": "Agent runner live!",
        "prompt_sent": prompt,
        "response": llm_text,
        "model": llm_model,
        "trust_score": trust_info["trust_score"],
        "risk_level": trust_info["risk_level"],
        "risk_flags": trust_info["risk_flags"],
        "explainability": trust_info["explanation"],
    }
