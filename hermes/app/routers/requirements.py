from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import verify_api_key
from ..models.schemas import RequirementCreate, RequirementResponse
from ..services.repository import repo

router = APIRouter(
    prefix="/projects",
    tags=["Requirements"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("/{project_id}/requirements", response_model=RequirementResponse, status_code=status.HTTP_201_CREATED)
async def create_requirement(project_id: UUID, payload: RequirementCreate):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        # Check if ID already exists
        existing = repo.get_requirement(payload.id)
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"Requirement with ID '{payload.id}' already exists."
            )

        # Create in db
        req = repo.create_requirement(
            id=payload.id,
            project_id=project_id,
            content=payload.content,
            status=payload.status
        )
        
        # Index in memory items
        repo.create_memory_item(
            project_id=project_id,
            type="requirement",
            title=f"Requirement {payload.id}",
            content=f"Requirement: {payload.content}",
            source="user",
            confidence=1.0,
            status=payload.status
        )
        
        return req
    except HTTPException as he:
        raise he
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/requirements", response_model=List[RequirementResponse])
async def list_requirements(project_id: UUID):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    try:
        return repo.list_requirements(project_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
