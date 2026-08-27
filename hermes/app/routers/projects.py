from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from ..dependencies import verify_api_key
from ..models.schemas import ProjectCreate, ProjectResponse, StateUpdate, StateResponse
from ..services.repository import repo

router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
    dependencies=[Depends(verify_api_key)]
)

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
async def create_project(payload: ProjectCreate):
    try:
        project = repo.create_project(
            name=payload.name,
            status=payload.status,
            current_phase_id=payload.current_phase_id
        )
        if not project:
            raise HTTPException(status_code=500, detail="Failed to create project")
        return project
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("", response_model=List[ProjectResponse])
async def list_projects():
    try:
        return repo.list_projects()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{project_id}/state", response_model=StateResponse)
async def get_project_state(project_id: UUID):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        state = repo.get_project_state(project_id)
        if not state:
            # If no state row exists, initialize it dynamically
            state = repo.create_initial_state(project_id)
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{project_id}/state", response_model=StateResponse)
async def update_project_state(project_id: UUID, payload: StateUpdate):
    project = repo.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    try:
        state_dict = payload.model_dump(exclude_unset=True)
        state = repo.update_project_state(project_id, state_dict)
        if not state:
            raise HTTPException(status_code=500, detail="Failed to update project state")
        return state
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
