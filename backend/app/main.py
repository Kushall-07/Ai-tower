from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .db.database import init_db
from .routes.agent import router as agent_router
from .routes.policy import router as policy_router
from .routes.action import router as action_router
from .routes.logs import router as logs_router
from .routes.approvals import router as approvals_router

app = FastAPI(
    title="AI Control Tower Backend",
    version="1.0.0",
)

# Allow frontend running on localhost:3000 (Next.js)
origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    init_db()


app.include_router(agent_router, prefix="/agent", tags=["Agent"])
app.include_router(policy_router, prefix="/policy", tags=["Policy"])
app.include_router(action_router, prefix="/action", tags=["Action"])
app.include_router(logs_router, prefix="/logs", tags=["Logs"])
app.include_router(approvals_router, prefix="/approvals", tags=["Approvals"])


@app.get("/")
def root():
    return {"message": "AI Control Tower Backend Running!"}
