from fastapi import APIRouter

router = APIRouter()

@router.post("/check")
def check_policy(data: dict):
    return {"status": "ok", "policy_check": "not implemented yet"}
