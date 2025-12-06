from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import init_db
from app.routes.agent import router as agent_router
from app.routes.logs import router as logs_router
from app.routes.approvals import router as approvals_router
from app.routes.actions import router as actions_router


app = FastAPI(title="AI Control Tower")


# CORS CONFIG
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
    # Create tables if not exist
    init_db()


# ROUTERS
app.include_router(agent_router)
app.include_router(logs_router)
app.include_router(approvals_router)
app.include_router(actions_router)


@app.get("/")
def root():
    return {"status": "ok", "service": "ai-control-tower-backend"}
