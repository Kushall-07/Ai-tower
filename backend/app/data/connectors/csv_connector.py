from pathlib import Path
from typing import List, Dict, Any
import csv


def load_csv(path: str) -> List[Dict[str, Any]]:
    """
    Load a CSV file into a list of dict rows.
    Safe for small / medium files.
    """
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"CSV file not found: {p}")

    rows: List[Dict[str, Any]] = []
    with p.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(dict(row))
    return rows
