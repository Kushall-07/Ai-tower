from fastapi import FastAPI

from .routes.agent import router as agent_router
from .routes.policy import router as policy_router
from .routes.action import router as action_router

app = FastAPI(
    title="AI Control Tower Backend",
    version="1.0.0",
)

# Include routes
app.include_router(agent_router, prefix="/agent", tags=["Agent"])
app.include_router(policy_router, prefix="/policy", tags=["Policy"])
app.include_router(action_router, prefix="/action", tags=["Action"])


@app.get("/")
def root():
    return {"message": "AI Control Tower Backend Running!"}
