from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.data.data_os import (
    run_query,
    list_source_datasets,
    get_available_sources,
    DataOSError,
)

router = APIRouter(prefix="/data", tags=["data-os"])


class DataQueryRequest(BaseModel):
    source: str  # "csv" for now
    dataset: str  # e.g. "customers"
    operation: str  # "preview" | "filter"
    filters: Optional[Dict[str, Any]] = None
    limit: int = 50


class DataQueryResponse(BaseModel):
    source: str
    dataset: str
    operation: str
    limit: int
    row_count: int
    rows: List[Dict[str, Any]]


class DataSourcesResponse(BaseModel):
    sources: List[str]


class DatasetsResponse(BaseModel):
    source: str
    datasets: List[str]


@router.get("/sources", response_model=DataSourcesResponse)
def get_sources():
    return DataSourcesResponse(sources=get_available_sources())


@router.get("/datasets", response_model=DatasetsResponse)
def get_datasets(source: str):
    """
    Example: GET /data/datasets?source=csv
    """
    try:
        datasets = list_source_datasets(source)
    except DataOSError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return DatasetsResponse(source=source, datasets=datasets)


@router.post("/query", response_model=DataQueryResponse)
def query_data(payload: DataQueryRequest):
    """
    Main Data OS entry point for clients/agents.

    Example body:
    {
      "source": "csv",
      "dataset": "customers",
      "operation": "filter",
      "filters": {"city": "Bangalore"},
      "limit": 20
    }
    """
    try:
        result = run_query(
            source=payload.source,
            dataset=payload.dataset,
            operation=payload.operation,
            filters=payload.filters,
            limit=payload.limit,
        )
    except DataOSError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Dataset file not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Data query error: {e}")

    return DataQueryResponse(**result)
