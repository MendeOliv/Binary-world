from typing import List, Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from ..dependencies import verify_api_key
from ..models.schemas import ConflictCreate, ConflictResponse
from ..services.repository import repo

router = APIRouter(
    prefix="/projects",
    tags=["Conflicts"],
    dependencies=[Depends(verify_api_key)]
)

@router.get("/{project_id}/conflicts", response_model=List[ConflictResponse])
async def list_conflicts(
    project_id: UUID,
    resolved: Optional[bool] = Query(default=None, description="Filter by resolved status")
):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return repo.list_conflicts(project_id, resolved=resolved)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{project_id}/conflicts", response_model=ConflictResponse, status_code=status.HTTP_201_CREATED)
async def create_conflict(project_id: UUID, payload: ConflictCreate):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        conflict = repo.create_conflict(
            project_id=project_id,
            item_a_id=payload.item_a_id,
            item_b_id=payload.item_b_id,
            description=payload.description
        )
        return conflict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{project_id}/conflicts/{conflict_id}", response_model=ConflictResponse)
async def resolve_conflict(project_id: UUID, conflict_id: UUID, resolution: str):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        updated = repo.resolve_conflict(conflict_id, resolution)
        if not updated:
            raise HTTPException(status_code=404, detail="Conflict not found")
        return updated
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
