from typing import Any, Dict, List, Optional

from app.data.connectors.csv_connector import (
    list_datasets,
    preview_dataset,
    filter_dataset,
)


class DataOSError(Exception):
    pass


def get_available_sources() -> List[str]:
    """
    For now we only support 'csv', but this makes it extensible.
    """
    return ["csv"]


def list_source_datasets(source: str) -> List[str]:
    """
    List datasets for a given source.
    For v1, only 'csv' is implemented.
    """
    if source != "csv":
        raise DataOSError(f"Unsupported source: {source}")
    return list_datasets()


def run_query(
    source: str,
    dataset: str,
    operation: str,
    filters: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> Dict[str, Any]:
    """
    Main Data OS entry point.

    Parameters:
      - source: "csv" (for now)
      - dataset: logical dataset name, e.g. "customers"
      - operation: "preview" | "filter"
      - filters: dict of equality filters (for 'filter')
      - limit: number of rows to return

    Returns:
      {
        "source": "csv",
        "dataset": "customers",
        "operation": "filter",
        "limit": 50,
        "rows": [...],
        "row_count": <int>
      }
    """
    if source != "csv":
        raise DataOSError(f"Unsupported source: {source}")

    if operation == "preview":
        rows = preview_dataset(dataset, limit=limit)
    elif operation == "filter":
        rows = filter_dataset(dataset, filters=filters or {}, limit=limit)
    else:
        raise DataOSError(f"Unsupported operation: {operation}")

    return {
        "source": source,
        "dataset": dataset,
        "operation": operation,
        "limit": limit,
        "row_count": len(rows),
        "rows": rows,
    }
