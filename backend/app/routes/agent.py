from fastapi import APIRouter
from ..llm.client import safe_generate

router = APIRouter()

@router.post("/run")
def run_agent(data: dict):
    """
    Simple Day-2 agent route.
    Calls secure LLM wrapper and returns output + placeholder trust_score.
    """
    prompt = data.get("prompt", "")

    # Call secure LLM wrapper
    output = safe_generate(prompt)

    # Placeholder trust score for now
    trust_score = 0.8

    return {
        "status": "ok",
        "message": "Agent runner live!",
        "prompt_sent": prompt,
        "response": output,
        "trust_score": trust_score,
    }
