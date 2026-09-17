"""FastAPI routes for CodeMigrate API."""

from fastapi import APIRouter, HTTPException
from app.schemas.analysis import AnalysisRequest, AnalysisResponse
from app.service import CodeMigrateService

router = APIRouter()
service = CodeMigrateService()


@router.on_event("startup")
def startup_event():
    service.initialize()


@router.post("/analyze", response_model=AnalysisResponse)
def analyze_endpoint(request: AnalysisRequest):
    """Analyze Python/Django code for breaking changes across target versions."""
    try:
        return service.analyze(request)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
