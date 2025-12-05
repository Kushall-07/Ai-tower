from typing import List, Dict, Any, Optional

from sqlmodel import Session, select

from ..db.database import engine
from ..db.models import AgentRun
from .connectors.csv_connector import load_csv


# ---- LOGS (AgentRun) helpers ----

def get_logs(
    limit: int = 100,
    risk_level: Optional[str] = None,
    policy_decision: Optional[str] = None,
) -> List[AgentRun]:
    """
    Query AgentRun logs with optional filters.
    This is the core of the Control Tower Data OS for now.
    """
    with Session(engine) as session:
        stmt = select(AgentRun).order_by(AgentRun.created_at.desc()).limit(limit)

        # Simple filters
        if risk_level:
            stmt = stmt.where(AgentRun.risk_level == risk_level)
        if policy_decision:
            stmt = stmt.where(AgentRun.policy_decision == policy_decision)

        results = session.exec(stmt).all()
        return list(results)


def get_logs_stats() -> Dict[str, Any]:
    """
    Compute basic analytics from AgentRun logs:
      - total_runs
      - by_risk_level
      - by_policy_decision
    """
    with Session(engine) as session:
        stmt = select(AgentRun)
        runs = session.exec(stmt).all()

    total = len(runs)
    by_risk: Dict[str, int] = {}
    by_policy: Dict[str, int] = {}

    for r in runs:
        by_risk[r.risk_level] = by_risk.get(r.risk_level, 0) + 1
        by_policy[r.policy_decision] = by_policy.get(r.policy_decision, 0) + 1

    return {
        "total_runs": total,
        "by_risk_level": by_risk,
        "by_policy_decision": by_policy,
    }


# ---- CSV / external data helpers (for future expansion) ----

def load_csv_dataset(path: str) -> List[Dict[str, Any]]:
    """
    Wrapper around the CSV connector.
    Later you can add caching, schema, etc.
    """
    return load_csv(path)
