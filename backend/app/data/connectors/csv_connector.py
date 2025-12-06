import csv
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.core.config import settings


def _get_csv_path(dataset_name: str) -> Path:
    """
    Map a logical dataset name (e.g. 'customers') to a real file path.
    Only allows datasets defined in settings.CSV_DATASETS.
    """
    if dataset_name not in settings.CSV_DATASETS:
        raise ValueError(f"Unknown dataset: {dataset_name}")

    base_dir = Path(settings.DATA_BASE_DIR)
    file_name = settings.CSV_DATASETS[dataset_name]
    return base_dir / file_name


def list_datasets() -> List[str]:
    """
    Return the list of logical dataset names.
    """
    return list(settings.CSV_DATASETS.keys())


def preview_dataset(dataset_name: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Return the first 'limit' rows of the dataset as a list of dicts.
    """
    path = _get_csv_path(dataset_name)
    rows: List[Dict[str, Any]] = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            rows.append(row)

    return rows


def filter_dataset(
    dataset_name: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> List[Dict[str, Any]]:
    """
    Apply simple equality-based filters like {"city": "Bangalore"} to the dataset.
    Returns up to 'limit' rows.
    """
    path = _get_csv_path(dataset_name)
    if filters is None:
        filters = {}

    rows: List[Dict[str, Any]] = []

    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            match = True
            for key, value in filters.items():
                # if column not in row or value doesn't match, skip
                if key not in row:
                    match = False
                    break
                if str(row[key]).strip() != str(value).strip():
                    match = False
                    break
            if match:
                rows.append(row)
                if len(rows) >= limit:
                    break

    return rows
