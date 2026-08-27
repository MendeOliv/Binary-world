from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from ..dependencies import verify_api_key
from ..models.schemas import RequestLogResponse
from ..services.repository import repo

router = APIRouter(
    prefix="/projects",
    tags=["Audit Logs"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/{project_id}/logs", response_model=List[RequestLogResponse])
async def list_project_logs(project_id: UUID):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return repo.list_request_logs(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
